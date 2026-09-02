"""add concurrency query indexes

Revision ID: f3c8d1a74e20
Revises: e12a7c9d4b10
"""
from alembic import op
revision="f3c8d1a74e20";down_revision="e12a7c9d4b10";branch_labels=None;depends_on=None
def upgrade():
    op.create_index("ix_attempt_student_status","exam_attempts",["student_id","status"])
    op.create_index("ix_attempt_exam_status_activity","exam_attempts",["exam_id","status","last_activity_at"])
    op.create_index("ix_exam_institute_status","exams",["institute_id","status"])
    op.create_index("ix_event_attempt_created","attempt_events",["attempt_id","created_at"])
def downgrade():
    op.drop_index("ix_event_attempt_created",table_name="attempt_events");op.drop_index("ix_exam_institute_status",table_name="exams");op.drop_index("ix_attempt_exam_status_activity",table_name="exam_attempts");op.drop_index("ix_attempt_student_status",table_name="exam_attempts")
