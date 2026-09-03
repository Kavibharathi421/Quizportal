from datetime import date, timedelta

from . import create_app, db
from .models import Exam, Institute, Question, QuestionOption, StudentCategory, StudentProfile, User, now

INSTITUTE_SLUG = "axiom"
CATEGORY_NAMES = [
    "Government / Internship Student", "Regular Course Student",
    "Intern Student", "Workshop Student", "Normal Student",
]
ADMIN_EMAIL = "admin@123.com"
STUDENT_EMAIL = "student@quizportal.test"
EXAM_TITLE = "Web Development Fundamentals"


def get_or_create(model, defaults=None, **filters):
    instance = model.query.filter_by(**filters).first()
    if instance is not None:
        return instance, False
    instance = model(**filters, **(defaults or {}))
    db.session.add(instance)
    db.session.flush()
    return instance, True


def seed():
    app = create_app()
    with app.app_context():
        # Run migrations before seeding. This also supports a brand-new dev DB.
        db.create_all()
        try:
            institute, _ = get_or_create(
                Institute, slug=INSTITUTE_SLUG,
                defaults={"name": "Axiom Learning Institute"},
            )

            categories = {}
            for name in CATEGORY_NAMES:
                category, _ = get_or_create(
                    StudentCategory, institute_id=institute.id, name=name
                )
                categories[name] = category

            # Repair the typo produced by older versions of this seed.
            admin = User.query.filter_by(email=ADMIN_EMAIL).first()
            legacy_admin = User.query.filter_by(email="admin@123,com").first()
            if admin is None and legacy_admin is not None:
                legacy_admin.email = ADMIN_EMAIL
                admin = legacy_admin
            if admin is None:
                admin = User(
                    name="Portal Administrator", email=ADMIN_EMAIL, role="ADMIN",
                    email_verified=True, institute_id=institute.id,
                )
                admin.set_password("Admin@123")
                db.session.add(admin)
                db.session.flush()

            student = User.query.filter_by(email=STUDENT_EMAIL).first()
            if student is None:
                student = User(
                    name="Aarav Sharma", email=STUDENT_EMAIL, role="STUDENT",
                    email_verified=True, institute_id=institute.id,
                )
                student.set_password("Student@123")
                db.session.add(student)
                db.session.flush()

            if StudentProfile.query.filter_by(user_id=student.id).first() is None:
                db.session.add(StudentProfile(
                    user=student, student_id="STU-1001",
                    course="Full Stack Development",
                    student_category_id=categories["Regular Course Student"].id,
                    enrollment_date=date.today() - timedelta(days=120),
                ))
                db.session.flush()

            exam = Exam.query.filter_by(
                institute_id=institute.id, title=EXAM_TITLE
            ).first()
            if exam is None:
                exam = Exam(
                    title=EXAM_TITLE,
                    description="HTML, CSS and JavaScript essentials.",
                    exam_category="Technical",
                    student_category_id=categories["Regular Course Student"].id,
                    institute_id=institute.id, duration=20, total_marks=10,
                    passing_percentage=50, start_at=now() - timedelta(days=1),
                    end_at=now() + timedelta(days=30), status="PUBLISHED",
                    created_by=admin.id, published_at=now(),
                )
                db.session.add(exam)
                db.session.flush()

            question_data = [
                ("Which language styles web pages?", ["HTML", "CSS", "Python", "SQL"], 1),
                ("JavaScript runs natively in a browser.", ["True", "False"], 0),
            ]
            for order, (text, options, correct_index) in enumerate(question_data, start=1):
                question = Question.query.filter_by(
                    exam_id=exam.id, question_order=order
                ).first()
                if question is None:
                    question = Question(
                        exam=exam, question_type="SINGLE", question_text=text,
                        marks=5, question_order=order,
                    )
                    db.session.add(question)
                    db.session.flush()
                for option_order, option_text in enumerate(options, start=1):
                    option = QuestionOption.query.filter_by(
                        question_id=question.id, option_order=option_order
                    ).first()
                    if option is None:
                        db.session.add(QuestionOption(
                            question=question, option_text=option_text,
                            is_correct=(option_order - 1 == correct_index),
                            option_order=option_order,
                        ))

            db.session.commit()
            print("Database seed completed successfully")
            print(f"Admin login: {ADMIN_EMAIL}")
            print(f"Student login: {STUDENT_EMAIL}")
        except Exception:
            db.session.rollback()
            raise


if __name__ == "__main__":
    seed()
