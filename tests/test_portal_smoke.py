import unittest
from datetime import timedelta
from io import BytesIO
from tempfile import TemporaryDirectory

from config import Config
from src import create_app, db
from src.models import Institute, Question, QuestionOption, StudentCategory, StudentProfile, User, now


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    JWT_SECRET_KEY = "test-jwt-secret-at-least-32-bytes-long"
    SECRET_KEY = "test-app-secret-at-least-32-bytes-long"
    RATELIMIT_ENABLED = False
    MAIL_SERVER = None
    SITE_URL = "http://localhost:5173"


class PortalSmokeTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.uploads = TemporaryDirectory()
        self.app.config["UPLOAD_FOLDER"] = self.uploads.name
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()

        institute = Institute(name="Test Institute", slug="test-institute")
        other_institute = Institute(name="Other Institute", slug="other-institute")
        db.session.add_all([institute, other_institute])
        db.session.flush()
        category = StudentCategory(name="Intern Student", institute_id=institute.id)
        other_category = StudentCategory(name="Intern Student", institute_id=other_institute.id)
        db.session.add_all([category, other_category])
        db.session.flush()

        admin = User(name="Test Admin", email="admin@test.local", role="ADMIN", status="ACTIVE", email_verified=True, institute_id=institute.id)
        admin.set_password("AdminPass123")
        student = User(name="Test Student", email="student@test.local", role="STUDENT", status="ACTIVE", email_verified=True, institute_id=institute.id)
        student.set_password("StudentPass123")
        other_admin = User(name="Other Admin", email="other-admin@test.local", role="ADMIN", status="ACTIVE", email_verified=True, institute_id=other_institute.id)
        other_admin.set_password("OtherPass123")
        db.session.add_all([admin, student, other_admin])
        db.session.flush()
        db.session.add(StudentProfile(user_id=student.id, student_id="TEST-001", course="Web Development", student_category_id=category.id, enrollment_date=now().date()))
        db.session.commit()

        self.institute_id = institute.id
        self.category_id = category.id
        self.student_id = student.id
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()
        self.uploads.cleanup()

    def data(self, response, status=200):
        self.assertEqual(response.status_code, status, response.get_json())
        return response.get_json()["data"]

    def login(self, role, identifier, password):
        result = self.data(self.client.post(f"/api/auth/{role}/login", json={"identifier": identifier, "password": password}))
        return {"Authorization": f"Bearer {result['token']}"}

    def test_complete_portal_flow(self):
        institutes = self.data(self.client.get("/api/auth/institutes"))
        self.assertEqual({item["name"] for item in institutes}, {"Test Institute", "Other Institute"})
        categories = self.data(self.client.get(f"/api/auth/student/categories?institute_id={self.institute_id}"))
        self.assertEqual([item["name"] for item in categories], ["Intern Student"])

        registration = self.data(self.client.post("/api/auth/student/register", json={
            "name": "New Student", "email": "new@test.local", "student_id": "TEST-002",
            "course": "Python", "institute_id": self.institute_id,
            "student_category_id": self.category_id, "password": "NewStudent123",
        }), 201)
        self.assertEqual(registration["status"], "PENDING")
        self.assertFalse(registration["email_verification_required"])

        admin_headers = self.login("admin", "admin@test.local", "AdminPass123")
        student_headers = self.login("student", "TEST-001", "StudentPass123")

        created = self.data(self.client.post("/api/admin/exams", headers=admin_headers, json={
            "title": "Intern Assessment", "description": "Phase smoke test",
            "exam_category": "Technical", "audience_mode": "students",
            "assigned_student_ids": [self.student_id], "duration": 30,
            "total_marks": 10, "passing_percentage": 50,
            "start_at": (now() - timedelta(minutes=5)).isoformat(),
            "end_at": (now() + timedelta(hours=1)).isoformat(),
            "questions": [{"text": "Which value is correct?", "type": "SINGLE", "marks": 10,
                           "options": [{"text": "Correct", "correct": True}, {"text": "Wrong", "correct": False}]}],
        }), 201)
        exam_id = created["id"]
        question = created["question_list"][0]
        correct_option = question["options"][0]["id"]
        self.assertEqual(created["target_category"], "1 selected student")

        edited = self.data(self.client.put(f"/api/admin/exams/{exam_id}", headers=admin_headers, json={"description": "Updated description"}))
        self.assertEqual(edited["description"], "Updated description")
        self.data(self.client.post(f"/api/admin/exams/{exam_id}/publish", headers=admin_headers, json={}))

        available = self.data(self.client.get("/api/student/exams", headers=student_headers))
        self.assertEqual([exam["id"] for exam in available], [exam_id])

        started = self.data(self.client.post(f"/api/student/exams/{exam_id}/start", headers=student_headers))
        attempt_id = started["attempt_id"]
        self.assertEqual(started["saved_answers"], {})
        saved = self.data(self.client.post(f"/api/student/attempts/{attempt_id}/answers", headers=student_headers, json={"question_id": question["id"], "answer": correct_option}))
        self.assertTrue(saved["saved"])

        resumed = self.data(self.client.post(f"/api/student/exams/{exam_id}/start", headers=student_headers))
        self.assertEqual(resumed["saved_answers"][str(question["id"])], correct_option)

        result = self.data(self.client.post(f"/api/student/attempts/{attempt_id}/submit", headers=student_headers))
        self.assertEqual(result["result"], "PASS")
        self.assertEqual(result["percentage"], 100)
        duplicate = self.data(self.client.post(f"/api/student/attempts/{attempt_id}/submit", headers=student_headers))
        self.assertEqual(duplicate["id"], attempt_id)
        self.assertEqual(duplicate["percentage"], 100)
        self.assertEqual(self.data(self.client.get("/api/student/exams", headers=student_headers)), [])
        repeated = self.data(self.client.post(f"/api/student/exams/{exam_id}/start", headers=student_headers))
        self.assertTrue(repeated["completed"])
        self.assertEqual(repeated["result_id"], attempt_id)
        self.assertEqual(len(self.data(self.client.get("/api/student/history", headers=student_headers))), 1)
        self.assertEqual(self.data(self.client.get(f"/api/student/results/{attempt_id}", headers=student_headers))["correct_answers"], 1)

        report = self.data(self.client.get(f"/api/admin/exams/{exam_id}/report", headers=admin_headers))
        self.assertEqual(report["summary"]["attended"], 1)
        self.assertEqual(report["summary"]["passed"], 1)
        self.data(self.client.post(f"/api/admin/exams/{exam_id}/complete",headers=admin_headers,json={}))
        missing_window=self.client.post(f"/api/admin/exams/{exam_id}/reactivate",headers=admin_headers,json={})
        self.assertEqual(missing_window.status_code,422)
        reactivated=self.data(self.client.post(f"/api/admin/exams/{exam_id}/reactivate",headers=admin_headers,json={"start_at":now().isoformat(),"end_at":(now()+timedelta(days=2)).isoformat()}))
        self.assertEqual(reactivated["status"],"PUBLISHED")
        reactivated_available=self.data(self.client.get("/api/student/exams",headers=student_headers))
        self.assertEqual([item["id"] for item in reactivated_available],[exam_id])
        second_cycle=self.data(self.client.post(f"/api/student/exams/{exam_id}/start",headers=student_headers))
        self.assertEqual(second_cycle["attempt_id"],attempt_id+1)
        self.assertEqual(len(self.data(self.client.get("/api/admin/history", headers=admin_headers))), 1)

        other_headers = self.login("admin", "other-admin@test.local", "OtherPass123")
        self.assertEqual(self.data(self.client.get("/api/admin/exams", headers=other_headers)), [])
        self.assertEqual(self.client.get(f"/api/admin/exams/{exam_id}/report", headers=other_headers).status_code, 404)

    def test_institute_management_and_limits(self):
        headers = self.login("admin", "admin@test.local", "AdminPass123")
        settings = self.data(self.client.get("/api/admin/institute", headers=headers))
        self.assertEqual(settings["usage"]["students"], 1)
        self.assertEqual(settings["subscription_status"], "TRIAL")

        updated = self.data(self.client.put("/api/admin/institute", headers=headers, json={"name": "Renamed Institute", "primary_color": "#123abc"}))
        self.assertEqual(updated["name"], "Renamed Institute")
        self.assertEqual(updated["primary_color"], "#123abc")
        self.assertEqual(self.client.put("/api/admin/institute", headers=headers, json={"name": "Bad", "primary_color": "red"}).status_code, 422)

        logo = self.data(self.client.post("/api/admin/institute/logo", headers=headers, data={"logo": (BytesIO(b"\x89PNG\r\n\x1a\n" + b"test-logo"), "logo.png")}, content_type="multipart/form-data"))
        self.assertIn("/api/uploads/institute-", logo["logo_url"])

        added = self.data(self.client.post("/api/admin/institute/administrators", headers=headers, json={"name": "Second Admin", "email": "second-admin@test.local", "password": "SecondAdmin123"}), 201)
        admins = self.data(self.client.get("/api/admin/institute/administrators", headers=headers))
        self.assertEqual(len(admins), 2)
        suspended = self.data(self.client.put(f"/api/admin/institute/administrators/{added['id']}/suspend", headers=headers, json={}))
        self.assertEqual(suspended["status"], "SUSPENDED")
        self.data(self.client.put(f"/api/admin/institute/administrators/{added['id']}/reactivate", headers=headers, json={}))
        current_id = next(item["id"] for item in admins if item["email"] == "admin@test.local")
        self.assertEqual(self.client.put(f"/api/admin/institute/administrators/{current_id}/suspend", headers=headers, json={}).status_code, 409)

        institute = db.session.get(Institute, self.institute_id)
        institute.student_limit = 1
        institute.exam_limit = 0
        db.session.commit()
        registration = self.client.post("/api/auth/student/register", json={"name": "Over Limit", "email": "limit@test.local", "student_id": "LIMIT-1", "course": "Test", "institute_id": self.institute_id, "student_category_id": self.category_id, "password": "LimitPass123"})
        self.assertEqual(registration.status_code, 409)
        exam = self.client.post("/api/admin/exams", headers=headers, json={"title": "Over Limit", "exam_category": "Test", "audience_mode": "category", "student_category_id": self.category_id, "duration": 10, "total_marks": 1, "passing_percentage": 50, "questions": []})
        self.assertEqual(exam.status_code, 409)

    def test_second_tab_switch_auto_submits_and_terminates_attempt(self):
        admin_headers = self.login("admin", "admin@test.local", "AdminPass123")
        student_headers = self.login("student", "TEST-001", "StudentPass123")
        created = self.data(self.client.post("/api/admin/exams", headers=admin_headers, json={
            "title": "Secure Assessment", "exam_category": "Technical", "audience_mode": "students",
            "assigned_student_ids": [self.student_id], "duration": 30, "total_marks": 10,
            "passing_percentage": 50, "start_at": (now() - timedelta(minutes=1)).isoformat(),
            "end_at": (now() + timedelta(hours=1)).isoformat(),
            "questions": [{"text": "Choose one", "type": "SINGLE", "marks": 10,
                           "options": [{"text": "Yes", "correct": True}, {"text": "No", "correct": False}]}],
        }), 201)
        self.data(self.client.post(f"/api/admin/exams/{created['id']}/publish", headers=admin_headers, json={}))
        attempt = self.data(self.client.post(f"/api/student/exams/{created['id']}/start", headers=student_headers))

        disconnected = self.data(self.client.post(f"/api/student/attempts/{attempt['attempt_id']}/events", headers=student_headers, json={"event_type": "PROLONGED_DISCONNECTION", "details": {"offline_seconds": 47}}))
        self.assertTrue(disconnected["recorded"])

        first = self.data(self.client.post(f"/api/student/attempts/{attempt['attempt_id']}/events", headers=student_headers, json={"event_type": "TAB_HIDDEN"}))
        self.assertEqual(first["action"], "WARNING")
        second = self.data(self.client.post(f"/api/student/attempts/{attempt['attempt_id']}/events", headers=student_headers, json={"event_type": "TAB_HIDDEN"}))
        self.assertEqual(second["action"], "TERMINATED")
        self.assertNotIn("percentage", second)
        self.assertEqual(self.data(self.client.get("/api/student/exams", headers=student_headers)), [])
        termination = self.data(self.client.get(f"/api/student/attempts/{attempt['attempt_id']}/termination", headers=student_headers))
        self.assertEqual(termination["status"], "TERMINATED")
        self.assertNotIn("termination_reason", termination)
        self.assertNotIn("percentage", termination)
        self.assertEqual(self.client.get(f"/api/student/results/{attempt['attempt_id']}", headers=student_headers).status_code, 404)

        monitoring = self.data(self.client.get("/api/admin/monitoring", headers=admin_headers))
        monitored = next(item for item in monitoring["attempts"] if item["id"] == attempt["attempt_id"])
        self.assertTrue(monitored["auto_submitted"])
        self.assertIn("tab-switch limit", monitored["termination_reason"])
        tab_events = [event for event in monitored["events"] if event["type"] == "TAB_HIDDEN"]
        self.assertEqual(sorted(event["details"]["switch_count"] for event in tab_events), [1, 2])
        disconnect_event = next(event for event in monitored["events"] if event["type"] == "PROLONGED_DISCONNECTION")
        self.assertEqual(disconnect_event["details"]["offline_seconds"], 47)
        logs = self.data(self.client.get("/api/admin/audit-logs?action=AUTO_TERMINATE_ATTEMPT", headers=admin_headers))
        self.assertEqual(logs["pagination"]["total"], 1)

    def test_public_institute_onboarding(self):
        created = self.data(self.client.post("/api/auth/institutes/onboard", json={"institute_name": "New Academy", "slug": "new-academy", "admin_name": "New Owner", "email": "owner@new.local", "password": "OwnerPass123"}), 201)
        self.assertEqual(created["institute"]["subscription_status"], "TRIAL")
        self.assertEqual(created["institute"]["student_limit"], 200)
        login = self.client.post("/api/auth/admin/login", json={"identifier": "owner@new.local", "password": "OwnerPass123"})
        self.assertEqual(login.status_code, 200, login.get_json())

    def test_health_and_request_id(self):
        response=self.client.get("/api/health/live",headers={"X-Request-ID":"test-correlation-id"})
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.headers["X-Request-ID"],"test-correlation-id")


if __name__ == "__main__":
    unittest.main()
