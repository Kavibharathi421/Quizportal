"""advanced exam features

Revision ID: a6f2c9d81044
Revises: f3c8d1a74e20
"""
from alembic import op
import sqlalchemy as sa

revision="a6f2c9d81044";down_revision="f3c8d1a74e20";branch_labels=None;depends_on=None

def upgrade():
    with op.batch_alter_table("exams") as b:
        b.add_column(sa.Column("tab_switch_limit",sa.Integer(),nullable=False,server_default="1"));b.add_column(sa.Column("enforce_fullscreen",sa.Boolean(),nullable=False,server_default=sa.false()));b.add_column(sa.Column("allow_copy_paste",sa.Boolean(),nullable=False,server_default=sa.false()));b.add_column(sa.Column("show_terminated_score",sa.Boolean(),nullable=False,server_default=sa.false()));b.add_column(sa.Column("security_warning_text",sa.String(500)));b.add_column(sa.Column("disconnection_grace_seconds",sa.Integer(),nullable=False,server_default="30"));b.add_column(sa.Column("result_publish_mode",sa.String(20),nullable=False,server_default="IMMEDIATE"));b.add_column(sa.Column("results_published_at",sa.DateTime(timezone=True)));b.add_column(sa.Column("hide_answers_until_close",sa.Boolean(),nullable=False,server_default=sa.true()));b.add_column(sa.Column("randomize_questions",sa.Boolean(),nullable=False,server_default=sa.false()));b.add_column(sa.Column("randomize_options",sa.Boolean(),nullable=False,server_default=sa.false()));b.add_column(sa.Column("version_count",sa.Integer(),nullable=False,server_default="1"))
    with op.batch_alter_table("questions") as b:b.add_column(sa.Column("topic",sa.String(120)));b.add_column(sa.Column("difficulty",sa.String(20),nullable=False,server_default="MEDIUM"));b.add_column(sa.Column("tags",sa.JSON()))
    with op.batch_alter_table("exam_attempts") as b:b.add_column(sa.Column("evaluation_status",sa.String(20),nullable=False,server_default="AUTO_GRADED"));b.add_column(sa.Column("result_published_at",sa.DateTime(timezone=True)));b.add_column(sa.Column("question_order",sa.JSON()));b.add_column(sa.Column("option_orders",sa.JSON()))
    with op.batch_alter_table("attempt_answers") as b:b.add_column(sa.Column("manual_marks",sa.Float()));b.add_column(sa.Column("evaluator_feedback",sa.Text()));b.add_column(sa.Column("evaluated_by",sa.Integer()));b.add_column(sa.Column("evaluated_at",sa.DateTime(timezone=True)));b.create_foreign_key("fk_answer_evaluator","users",["evaluated_by"],["id"])
    op.create_table("question_bank_items",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("institute_id",sa.Integer(),sa.ForeignKey("institutes.id"),nullable=False),sa.Column("question_type",sa.String(30),nullable=False),sa.Column("question_text",sa.Text(),nullable=False),sa.Column("marks",sa.Float(),nullable=False,server_default="1"),sa.Column("topic",sa.String(120)),sa.Column("difficulty",sa.String(20),nullable=False,server_default="MEDIUM"),sa.Column("tags",sa.JSON()),sa.Column("options",sa.JSON()),sa.Column("correct_answer",sa.JSON()),sa.Column("created_by",sa.Integer(),sa.ForeignKey("users.id"),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True)),sa.Column("updated_at",sa.DateTime(timezone=True)))
    op.create_index("ix_bank_institute","question_bank_items",["institute_id"]);op.create_index("ix_bank_topic","question_bank_items",["topic"]);op.create_index("ix_bank_difficulty","question_bank_items",["difficulty"])

def downgrade():
    op.drop_table("question_bank_items")
    with op.batch_alter_table("attempt_answers") as b:b.drop_constraint("fk_answer_evaluator",type_="foreignkey");b.drop_column("evaluated_at");b.drop_column("evaluated_by");b.drop_column("evaluator_feedback");b.drop_column("manual_marks")
    with op.batch_alter_table("exam_attempts") as b:b.drop_column("option_orders");b.drop_column("question_order");b.drop_column("result_published_at");b.drop_column("evaluation_status")
    with op.batch_alter_table("questions") as b:b.drop_column("tags");b.drop_column("difficulty");b.drop_column("topic")
    with op.batch_alter_table("exams") as b:
        for name in ("version_count","randomize_options","randomize_questions","hide_answers_until_close","results_published_at","result_publish_mode","disconnection_grace_seconds","security_warning_text","show_terminated_score","allow_copy_paste","enforce_fullscreen","tab_switch_limit"):b.drop_column(name)
