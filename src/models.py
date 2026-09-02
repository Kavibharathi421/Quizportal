from datetime import datetime, timezone
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

def now(): return datetime.now(timezone.utc)
def exam_code(): return secrets.token_hex(5).upper()

class Institute(db.Model):
    __tablename__="institutes"
    id=db.Column(db.Integer,primary_key=True); name=db.Column(db.String(160),nullable=False); slug=db.Column(db.String(80),unique=True,index=True,nullable=False); status=db.Column(db.String(20),default="ACTIVE",nullable=False)
    logo_url=db.Column(db.String(500)); primary_color=db.Column(db.String(20),default="#4169e1"); subscription_plan=db.Column(db.String(30),default="PILOT",nullable=False); subscription_status=db.Column(db.String(20),default="TRIAL",nullable=False)
    student_limit=db.Column(db.Integer,default=200,nullable=False); exam_limit=db.Column(db.Integer,default=50,nullable=False); subscription_ends_at=db.Column(db.DateTime(timezone=True)); created_at=db.Column(db.DateTime(timezone=True),default=now)

class User(db.Model):
    __tablename__="users"
    id=db.Column(db.Integer,primary_key=True); name=db.Column(db.String(120),nullable=False)
    email=db.Column(db.String(180),unique=True,index=True,nullable=False); password_hash=db.Column(db.String(255),nullable=False)
    role=db.Column(db.String(20),index=True,nullable=False); status=db.Column(db.String(20),default="ACTIVE",nullable=False); email_verified=db.Column(db.Boolean,default=False,nullable=False); institute_id=db.Column(db.Integer,db.ForeignKey("institutes.id"),index=True,nullable=False)
    created_at=db.Column(db.DateTime(timezone=True),default=now); updated_at=db.Column(db.DateTime(timezone=True),default=now,onupdate=now)
    institute=db.relationship("Institute"); profile=db.relationship("StudentProfile",back_populates="user",uselist=False,cascade="all, delete-orphan")
    def set_password(self,p): self.password_hash=generate_password_hash(p)
    def check_password(self,p): return check_password_hash(self.password_hash,p)

class AccountToken(db.Model):
    __tablename__="account_tokens"
    id=db.Column(db.Integer,primary_key=True); user_id=db.Column(db.Integer,db.ForeignKey("users.id"),index=True,nullable=False); purpose=db.Column(db.String(30),index=True,nullable=False); token_hash=db.Column(db.String(64),unique=True,index=True,nullable=False)
    expires_at=db.Column(db.DateTime(timezone=True),nullable=False); used_at=db.Column(db.DateTime(timezone=True)); created_at=db.Column(db.DateTime(timezone=True),default=now)
    user=db.relationship("User")

class StudentCategory(db.Model):
    __tablename__="student_categories"
    __table_args__=(db.UniqueConstraint("institute_id","name",name="uq_institute_category_name"),)
    id=db.Column(db.Integer,primary_key=True); name=db.Column(db.String(100),nullable=False); institute_id=db.Column(db.Integer,db.ForeignKey("institutes.id"),index=True,nullable=False); description=db.Column(db.String(255)); status=db.Column(db.String(20),default="ACTIVE")
    created_at=db.Column(db.DateTime(timezone=True),default=now)

class Course(db.Model):
    __tablename__="portal_courses";__table_args__=(db.UniqueConstraint("institute_id","name",name="uq_institute_course_name"),)
    id=db.Column(db.Integer,primary_key=True);institute_id=db.Column(db.Integer,db.ForeignKey("institutes.id"),index=True,nullable=False);name=db.Column(db.String(160),nullable=False);code=db.Column(db.String(50));description=db.Column(db.Text);status=db.Column(db.String(20),default="ACTIVE",nullable=False);created_at=db.Column(db.DateTime(timezone=True),default=now)

class Batch(db.Model):
    __tablename__="batches";__table_args__=(db.UniqueConstraint("institute_id","name",name="uq_institute_batch_name"),)
    id=db.Column(db.Integer,primary_key=True);institute_id=db.Column(db.Integer,db.ForeignKey("institutes.id"),index=True,nullable=False);course_id=db.Column(db.Integer,db.ForeignKey("portal_courses.id"),index=True,nullable=False);name=db.Column(db.String(160),nullable=False);start_date=db.Column(db.Date);end_date=db.Column(db.Date);trainer_name=db.Column(db.String(160));status=db.Column(db.String(20),default="ACTIVE",nullable=False);created_at=db.Column(db.DateTime(timezone=True),default=now);course=db.relationship("Course")

class StudentProfile(db.Model):
    __tablename__="student_profiles"
    id=db.Column(db.Integer,primary_key=True); user_id=db.Column(db.Integer,db.ForeignKey("users.id"),unique=True,nullable=False)
    student_id=db.Column(db.String(50),unique=True,index=True,nullable=False); course=db.Column(db.String(120)); course_id=db.Column(db.Integer,db.ForeignKey("portal_courses.id"),index=True);batch_id=db.Column(db.Integer,db.ForeignKey("batches.id"),index=True);student_category_id=db.Column(db.Integer,db.ForeignKey("student_categories.id"),nullable=False)
    enrollment_date=db.Column(db.Date,nullable=False); user=db.relationship("User",back_populates="profile"); category=db.relationship("StudentCategory");course_record=db.relationship("Course");batch=db.relationship("Batch")

class Exam(db.Model):
    __tablename__="exams"
    id=db.Column(db.Integer,primary_key=True); access_code=db.Column(db.String(10),unique=True,index=True,nullable=False,default=exam_code); title=db.Column(db.String(180),nullable=False); description=db.Column(db.Text); exam_category=db.Column(db.String(100),nullable=False)
    student_category_id=db.Column(db.Integer,db.ForeignKey("student_categories.id"));course_id=db.Column(db.Integer,db.ForeignKey("portal_courses.id"),index=True);batch_id=db.Column(db.Integer,db.ForeignKey("batches.id"),index=True); institute_id=db.Column(db.Integer,db.ForeignKey("institutes.id"),index=True,nullable=False); duration=db.Column(db.Integer,nullable=False); total_marks=db.Column(db.Float,nullable=False)
    passing_percentage=db.Column(db.Float,nullable=False); start_at=db.Column(db.DateTime(timezone=True)); end_at=db.Column(db.DateTime(timezone=True)); status=db.Column(db.String(20),default="DRAFT",index=True)
    created_by=db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False); published_at=db.Column(db.DateTime(timezone=True)); completed_at=db.Column(db.DateTime(timezone=True)); archived_at=db.Column(db.DateTime(timezone=True))
    created_at=db.Column(db.DateTime(timezone=True),default=now); updated_at=db.Column(db.DateTime(timezone=True),default=now,onupdate=now)
    tab_switch_limit=db.Column(db.Integer,default=1,nullable=False); enforce_fullscreen=db.Column(db.Boolean,default=False,nullable=False); allow_copy_paste=db.Column(db.Boolean,default=False,nullable=False); show_terminated_score=db.Column(db.Boolean,default=False,nullable=False); security_warning_text=db.Column(db.String(500)); disconnection_grace_seconds=db.Column(db.Integer,default=30,nullable=False)
    result_publish_mode=db.Column(db.String(20),default="IMMEDIATE",nullable=False); results_published_at=db.Column(db.DateTime(timezone=True)); hide_answers_until_close=db.Column(db.Boolean,default=True,nullable=False); randomize_questions=db.Column(db.Boolean,default=False,nullable=False); randomize_options=db.Column(db.Boolean,default=False,nullable=False); version_count=db.Column(db.Integer,default=1,nullable=False)
    category=db.relationship("StudentCategory"); assignments=db.relationship("ExamAssignment",back_populates="exam",cascade="all, delete-orphan"); questions=db.relationship("Question",back_populates="exam",order_by="Question.question_order",cascade="all, delete-orphan")
    attempts=db.relationship("ExamAttempt",back_populates="exam")

class ExamAssignment(db.Model):
    __tablename__="exam_assignments"; __table_args__=(db.UniqueConstraint("exam_id","student_id",name="uq_exam_assigned_student"),)
    id=db.Column(db.Integer,primary_key=True); exam_id=db.Column(db.Integer,db.ForeignKey("exams.id"),index=True,nullable=False); student_id=db.Column(db.Integer,db.ForeignKey("users.id"),index=True,nullable=False)
    assigned_by=db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False); created_at=db.Column(db.DateTime(timezone=True),default=now)
    exam=db.relationship("Exam",back_populates="assignments"); student=db.relationship("User",foreign_keys=[student_id])

class Question(db.Model):
    __tablename__="questions"
    id=db.Column(db.Integer,primary_key=True); exam_id=db.Column(db.Integer,db.ForeignKey("exams.id"),index=True,nullable=False); question_type=db.Column(db.String(30),nullable=False)
    question_text=db.Column(db.Text,nullable=False); marks=db.Column(db.Float,nullable=False); question_order=db.Column(db.Integer,nullable=False)
    topic=db.Column(db.String(120)); difficulty=db.Column(db.String(20),default="MEDIUM",nullable=False); tags=db.Column(db.JSON,default=list)
    exam=db.relationship("Exam",back_populates="questions"); options=db.relationship("QuestionOption",back_populates="question",order_by="QuestionOption.option_order",cascade="all, delete-orphan")

class QuestionOption(db.Model):
    __tablename__="question_options"
    id=db.Column(db.Integer,primary_key=True); question_id=db.Column(db.Integer,db.ForeignKey("questions.id"),index=True,nullable=False); option_text=db.Column(db.Text,nullable=False); is_correct=db.Column(db.Boolean,default=False); option_order=db.Column(db.Integer,nullable=False)
    question=db.relationship("Question",back_populates="options")

class ExamAttempt(db.Model):
    __tablename__="exam_attempts"; __table_args__=(db.UniqueConstraint("exam_id","student_id","attempt_number",name="uq_exam_student_number"),)
    id=db.Column(db.Integer,primary_key=True); exam_id=db.Column(db.Integer,db.ForeignKey("exams.id"),index=True,nullable=False); student_id=db.Column(db.Integer,db.ForeignKey("users.id"),index=True,nullable=False)
    attempt_number=db.Column(db.Integer,default=1,nullable=False); started_at=db.Column(db.DateTime(timezone=True),default=now); submitted_at=db.Column(db.DateTime(timezone=True)); status=db.Column(db.String(20),default="IN_PROGRESS",index=True)
    last_activity_at=db.Column(db.DateTime(timezone=True),default=now,index=True); extra_time_minutes=db.Column(db.Integer,default=0,nullable=False); paused_at=db.Column(db.DateTime(timezone=True)); paused_seconds=db.Column(db.Integer,default=0,nullable=False); auto_submitted=db.Column(db.Boolean,default=False,nullable=False)
    session_id=db.Column(db.String(80)); initial_ip=db.Column(db.String(64)); user_agent=db.Column(db.String(500)); refresh_count=db.Column(db.Integer,default=0,nullable=False); risk_score=db.Column(db.Integer,default=0,nullable=False); warning_message=db.Column(db.String(500)); warning_sent_at=db.Column(db.DateTime(timezone=True)); retake_allowed=db.Column(db.Boolean,default=False,nullable=False); retake_reason=db.Column(db.String(500)); termination_reason=db.Column(db.String(500))
    total_questions=db.Column(db.Integer,default=0); attempted_questions=db.Column(db.Integer,default=0); correct_answers=db.Column(db.Integer,default=0); wrong_answers=db.Column(db.Integer,default=0); unanswered_questions=db.Column(db.Integer,default=0)
    total_marks=db.Column(db.Float,default=0); obtained_marks=db.Column(db.Float,default=0); percentage=db.Column(db.Float,default=0); result=db.Column(db.String(10))
    evaluation_status=db.Column(db.String(20),default="AUTO_GRADED",nullable=False); result_published_at=db.Column(db.DateTime(timezone=True)); question_order=db.Column(db.JSON); option_orders=db.Column(db.JSON)
    exam=db.relationship("Exam",back_populates="attempts"); student=db.relationship("User"); answers=db.relationship("AttemptAnswer",back_populates="attempt",cascade="all, delete-orphan")
    events=db.relationship("AttemptEvent",back_populates="attempt",cascade="all, delete-orphan")

class AttemptEvent(db.Model):
    __tablename__="attempt_events"
    id=db.Column(db.Integer,primary_key=True); attempt_id=db.Column(db.Integer,db.ForeignKey("exam_attempts.id"),index=True,nullable=False); event_type=db.Column(db.String(40),index=True,nullable=False); severity=db.Column(db.String(20),default="INFO",nullable=False); risk_points=db.Column(db.Integer,default=0,nullable=False)
    details=db.Column(db.JSON); ip_address=db.Column(db.String(64)); user_agent=db.Column(db.String(500)); created_at=db.Column(db.DateTime(timezone=True),default=now,index=True); attempt=db.relationship("ExamAttempt",back_populates="events")

class AttemptAnswer(db.Model):
    __tablename__="attempt_answers"; __table_args__=(db.UniqueConstraint("attempt_id","question_id",name="uq_attempt_question"),)
    id=db.Column(db.Integer,primary_key=True); attempt_id=db.Column(db.Integer,db.ForeignKey("exam_attempts.id"),index=True,nullable=False); question_id=db.Column(db.Integer,db.ForeignKey("questions.id"),nullable=False)
    answer=db.Column(db.JSON); is_correct=db.Column(db.Boolean); marks_obtained=db.Column(db.Float,default=0); answered_at=db.Column(db.DateTime(timezone=True),default=now)
    manual_marks=db.Column(db.Float); evaluator_feedback=db.Column(db.Text); evaluated_by=db.Column(db.Integer,db.ForeignKey("users.id")); evaluated_at=db.Column(db.DateTime(timezone=True))
    attempt=db.relationship("ExamAttempt",back_populates="answers"); question=db.relationship("Question")

class QuestionBankItem(db.Model):
    __tablename__="question_bank_items"
    id=db.Column(db.Integer,primary_key=True);institute_id=db.Column(db.Integer,db.ForeignKey("institutes.id"),index=True,nullable=False);question_type=db.Column(db.String(30),nullable=False);question_text=db.Column(db.Text,nullable=False);marks=db.Column(db.Float,default=1,nullable=False);topic=db.Column(db.String(120),index=True);difficulty=db.Column(db.String(20),default="MEDIUM",index=True,nullable=False);tags=db.Column(db.JSON,default=list);options=db.Column(db.JSON,default=list);correct_answer=db.Column(db.JSON);created_by=db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False);created_at=db.Column(db.DateTime(timezone=True),default=now);updated_at=db.Column(db.DateTime(timezone=True),default=now,onupdate=now)

class AuditLog(db.Model):

    
    __tablename__="audit_logs"
    id=db.Column(db.Integer,primary_key=True); institute_id=db.Column(db.Integer,db.ForeignKey("institutes.id"),index=True); actor_id=db.Column(db.Integer,db.ForeignKey("users.id"),index=True); action=db.Column(db.String(80),nullable=False); category=db.Column(db.String(30),default="AUDIT",nullable=False); severity=db.Column(db.String(20),default="INFO",nullable=False); entity_type=db.Column(db.String(40)); entity_id=db.Column(db.Integer); details=db.Column(db.JSON); ip_address=db.Column(db.String(64)); user_agent=db.Column(db.String(500)); request_id=db.Column(db.String(64),index=True); created_at=db.Column(db.DateTime(timezone=True),default=now)
