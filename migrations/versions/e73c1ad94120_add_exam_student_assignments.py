"""add individual exam assignments

Revision ID: e73c1ad94120
Revises: a42b8e91c301
"""
from alembic import op
import sqlalchemy as sa

revision = "e73c1ad94120"
down_revision = "a42b8e91c301"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("exam_assignments",
        sa.Column("id",sa.Integer(),nullable=False),
        sa.Column("exam_id",sa.Integer(),nullable=False),
        sa.Column("student_id",sa.Integer(),nullable=False),
        sa.Column("assigned_by",sa.Integer(),nullable=False),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=True),
        sa.ForeignKeyConstraint(["assigned_by"],["users.id"]),
        sa.ForeignKeyConstraint(["exam_id"],["exams.id"]),
        sa.ForeignKeyConstraint(["student_id"],["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("exam_id","student_id",name="uq_exam_assigned_student"))
    op.create_index("ix_exam_assignments_exam_id","exam_assignments",["exam_id"])
    op.create_index("ix_exam_assignments_student_id","exam_assignments",["student_id"])

def downgrade():
    op.drop_index("ix_exam_assignments_student_id",table_name="exam_assignments")
    op.drop_index("ix_exam_assignments_exam_id",table_name="exam_assignments")
    op.drop_table("exam_assignments")
