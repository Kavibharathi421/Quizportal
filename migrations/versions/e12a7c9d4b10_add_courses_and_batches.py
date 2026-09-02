"""add courses and batches

Revision ID: e12a7c9d4b10
Revises: d95fa1b2e431
"""
from alembic import op
import sqlalchemy as sa

revision="e12a7c9d4b10"
down_revision="d95fa1b2e431"
branch_labels=None
depends_on=None

def upgrade():
    op.create_table("portal_courses",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("institute_id",sa.Integer(),sa.ForeignKey("institutes.id"),nullable=False),sa.Column("name",sa.String(160),nullable=False),sa.Column("code",sa.String(50)),sa.Column("description",sa.Text()),sa.Column("status",sa.String(20),nullable=False,server_default="ACTIVE"),sa.Column("created_at",sa.DateTime(timezone=True)),sa.UniqueConstraint("institute_id","name",name="uq_institute_course_name"));op.create_index("ix_portal_courses_institute_id","portal_courses",["institute_id"])
    op.create_table("batches",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("institute_id",sa.Integer(),sa.ForeignKey("institutes.id"),nullable=False),sa.Column("course_id",sa.Integer(),sa.ForeignKey("portal_courses.id"),nullable=False),sa.Column("name",sa.String(160),nullable=False),sa.Column("start_date",sa.Date()),sa.Column("end_date",sa.Date()),sa.Column("trainer_name",sa.String(160)),sa.Column("status",sa.String(20),nullable=False,server_default="ACTIVE"),sa.Column("created_at",sa.DateTime(timezone=True)),sa.UniqueConstraint("institute_id","name",name="uq_institute_batch_name"));op.create_index("ix_batches_institute_id","batches",["institute_id"]);op.create_index("ix_batches_course_id","batches",["course_id"])
    with op.batch_alter_table("student_profiles") as batch:batch.add_column(sa.Column("course_id",sa.Integer()));batch.add_column(sa.Column("batch_id",sa.Integer()));batch.create_foreign_key("fk_profiles_course","portal_courses",["course_id"],["id"]);batch.create_foreign_key("fk_profiles_batch","batches",["batch_id"],["id"]);batch.create_index("ix_student_profiles_course_id",["course_id"]);batch.create_index("ix_student_profiles_batch_id",["batch_id"])
    with op.batch_alter_table("exams") as batch:batch.add_column(sa.Column("course_id",sa.Integer()));batch.add_column(sa.Column("batch_id",sa.Integer()));batch.create_foreign_key("fk_exams_course","portal_courses",["course_id"],["id"]);batch.create_foreign_key("fk_exams_batch","batches",["batch_id"],["id"]);batch.create_index("ix_exams_course_id",["course_id"]);batch.create_index("ix_exams_batch_id",["batch_id"])

def downgrade():
    with op.batch_alter_table("exams") as batch:batch.drop_index("ix_exams_batch_id");batch.drop_index("ix_exams_course_id");batch.drop_constraint("fk_exams_batch",type_="foreignkey");batch.drop_constraint("fk_exams_course",type_="foreignkey");batch.drop_column("batch_id");batch.drop_column("course_id")
    with op.batch_alter_table("student_profiles") as batch:batch.drop_index("ix_student_profiles_batch_id");batch.drop_index("ix_student_profiles_course_id");batch.drop_constraint("fk_profiles_batch",type_="foreignkey");batch.drop_constraint("fk_profiles_course",type_="foreignkey");batch.drop_column("batch_id");batch.drop_column("course_id")
    op.drop_table("batches");op.drop_table("portal_courses")
