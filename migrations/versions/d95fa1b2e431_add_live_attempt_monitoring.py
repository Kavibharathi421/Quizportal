"""add live attempt monitoring

Revision ID: d95fa1b2e431
Revises: c84ec6f78d25
"""
from alembic import op
import sqlalchemy as sa

revision="d95fa1b2e431"
down_revision="c84ec6f78d25"
branch_labels=None
depends_on=None

def upgrade():
    with op.batch_alter_table("exam_attempts") as batch:
        batch.drop_constraint("uq_exam_student",type_="unique")
        batch.add_column(sa.Column("attempt_number",sa.Integer(),nullable=False,server_default="1"));batch.add_column(sa.Column("last_activity_at",sa.DateTime(timezone=True)));batch.add_column(sa.Column("extra_time_minutes",sa.Integer(),nullable=False,server_default="0"));batch.add_column(sa.Column("paused_at",sa.DateTime(timezone=True)));batch.add_column(sa.Column("paused_seconds",sa.Integer(),nullable=False,server_default="0"));batch.add_column(sa.Column("auto_submitted",sa.Boolean(),nullable=False,server_default=sa.false()));batch.add_column(sa.Column("session_id",sa.String(length=80)));batch.add_column(sa.Column("initial_ip",sa.String(length=64)));batch.add_column(sa.Column("user_agent",sa.String(length=500)));batch.add_column(sa.Column("refresh_count",sa.Integer(),nullable=False,server_default="0"));batch.add_column(sa.Column("risk_score",sa.Integer(),nullable=False,server_default="0"));batch.add_column(sa.Column("warning_message",sa.String(length=500)));batch.add_column(sa.Column("warning_sent_at",sa.DateTime(timezone=True)));batch.add_column(sa.Column("retake_allowed",sa.Boolean(),nullable=False,server_default=sa.false()));batch.add_column(sa.Column("retake_reason",sa.String(length=500)));batch.add_column(sa.Column("termination_reason",sa.String(length=500)));batch.create_unique_constraint("uq_exam_student_number",["exam_id","student_id","attempt_number"]);batch.create_index("ix_exam_attempts_last_activity_at",["last_activity_at"])
    op.execute("UPDATE exam_attempts SET last_activity_at=started_at")
    op.create_table("attempt_events",sa.Column("id",sa.Integer(),nullable=False),sa.Column("attempt_id",sa.Integer(),nullable=False),sa.Column("event_type",sa.String(length=40),nullable=False),sa.Column("severity",sa.String(length=20),nullable=False),sa.Column("risk_points",sa.Integer(),nullable=False),sa.Column("details",sa.JSON()),sa.Column("ip_address",sa.String(length=64)),sa.Column("user_agent",sa.String(length=500)),sa.Column("created_at",sa.DateTime(timezone=True)),sa.ForeignKeyConstraint(["attempt_id"],["exam_attempts.id"]),sa.PrimaryKeyConstraint("id"));op.create_index("ix_attempt_events_attempt_id","attempt_events",["attempt_id"]);op.create_index("ix_attempt_events_event_type","attempt_events",["event_type"]);op.create_index("ix_attempt_events_created_at","attempt_events",["created_at"])
    with op.batch_alter_table("audit_logs") as batch:
        batch.add_column(sa.Column("institute_id",sa.Integer()));batch.add_column(sa.Column("category",sa.String(length=30),nullable=False,server_default="AUDIT"));batch.add_column(sa.Column("severity",sa.String(length=20),nullable=False,server_default="INFO"));batch.add_column(sa.Column("ip_address",sa.String(length=64)));batch.add_column(sa.Column("user_agent",sa.String(length=500)));batch.add_column(sa.Column("request_id",sa.String(length=64)));batch.create_foreign_key("fk_audit_logs_institute_id","institutes",["institute_id"],["id"]);batch.create_index("ix_audit_logs_institute_id",["institute_id"]);batch.create_index("ix_audit_logs_request_id",["request_id"])
    op.execute("UPDATE audit_logs a JOIN users u ON a.actor_id=u.id SET a.institute_id=u.institute_id WHERE a.institute_id IS NULL")

def downgrade():
    with op.batch_alter_table("audit_logs") as batch:
        batch.drop_index("ix_audit_logs_request_id");batch.drop_index("ix_audit_logs_institute_id");batch.drop_constraint("fk_audit_logs_institute_id",type_="foreignkey");batch.drop_column("request_id");batch.drop_column("user_agent");batch.drop_column("ip_address");batch.drop_column("severity");batch.drop_column("category");batch.drop_column("institute_id")
    op.drop_index("ix_attempt_events_created_at",table_name="attempt_events");op.drop_index("ix_attempt_events_event_type",table_name="attempt_events");op.drop_index("ix_attempt_events_attempt_id",table_name="attempt_events");op.drop_table("attempt_events")
    with op.batch_alter_table("exam_attempts") as batch:
        batch.drop_index("ix_exam_attempts_last_activity_at");batch.drop_constraint("uq_exam_student_number",type_="unique");batch.drop_column("termination_reason");batch.drop_column("retake_reason");batch.drop_column("retake_allowed");batch.drop_column("warning_sent_at");batch.drop_column("warning_message");batch.drop_column("risk_score");batch.drop_column("refresh_count");batch.drop_column("user_agent");batch.drop_column("initial_ip");batch.drop_column("session_id");batch.drop_column("auto_submitted");batch.drop_column("paused_seconds");batch.drop_column("paused_at");batch.drop_column("extra_time_minutes");batch.drop_column("last_activity_at");batch.drop_column("attempt_number");batch.create_unique_constraint("uq_exam_student",["exam_id","student_id"])
