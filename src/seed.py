from datetime import date, timedelta
from . import create_app, db
from .models import Institute, User, StudentCategory, StudentProfile, Exam, Question, QuestionOption, now

def seed():
    app=create_app()
    with app.app_context():
        db.create_all()
        if User.query.first(): print("Database already seeded"); return
        institute=Institute(name="Axiom Learning Institute",slug="axiom");db.session.add(institute);db.session.flush()
        cats=[StudentCategory(name=x,institute_id=institute.id) for x in ["Government / Internship Student","Regular Course Student","Intern Student","Workshop Student","Normal Student"]]
        db.session.add_all(cats);db.session.flush()
        admin=User(name="Portal Administrator",email="admin@123,com",role="ADMIN",email_verified=True,institute_id=institute.id);admin.set_password("Admin@123")
        student=User(name="Aarav Sharma",email="student@quizportal.test",role="STUDENT",email_verified=True,institute_id=institute.id);student.set_password("Student@123")
        db.session.add_all([admin,student]);db.session.flush();db.session.add(StudentProfile(user=student,student_id="STU-1001",course="Full Stack Development",student_category_id=cats[1].id,enrollment_date=date.today()-timedelta(days=120)));db.session.flush()
        e=Exam(title="Web Development Fundamentals",description="HTML, CSS and JavaScript essentials.",exam_category="Technical",student_category_id=cats[1].id,institute_id=institute.id,duration=20,total_marks=10,passing_percentage=50,start_at=now()-timedelta(days=1),end_at=now()+timedelta(days=30),status="PUBLISHED",created_by=admin.id,published_at=now())
        db.session.add(e);db.session.flush()
        for i,(text,opts,correct) in enumerate([("Which language styles web pages?",["HTML","CSS","Python","SQL"],1),("JavaScript runs natively in a browser.",["True","False"],0)]):
            q=Question(exam=e,question_type="SINGLE",question_text=text,marks=5,question_order=i+1);db.session.add(q);db.session.flush()
            for j,o in enumerate(opts):db.session.add(QuestionOption(question=q,option_text=o,is_correct=j==correct,option_order=j+1))
        db.session.commit();print("Seeded demo accounts")
if __name__=="__main__":seed()
