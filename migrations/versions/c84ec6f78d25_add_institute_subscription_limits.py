"""add institute subscription limits

Revision ID: c84ec6f78d25
Revises: b742ed5a1c63
"""
from alembic import op
import sqlalchemy as sa

revision="c84ec6f78d25"
down_revision="b742ed5a1c63"
branch_labels=None
depends_on=None

def upgrade():
    with op.batch_alter_table("institutes") as batch:
        batch.add_column(sa.Column("subscription_plan",sa.String(length=30),nullable=False,server_default="PILOT"))
        batch.add_column(sa.Column("subscription_status",sa.String(length=20),nullable=False,server_default="TRIAL"))
        batch.add_column(sa.Column("student_limit",sa.Integer(),nullable=False,server_default="200"))
        batch.add_column(sa.Column("exam_limit",sa.Integer(),nullable=False,server_default="50"))
        batch.add_column(sa.Column("subscription_ends_at",sa.DateTime(timezone=True),nullable=True))

def downgrade():
    with op.batch_alter_table("institutes") as batch:
        batch.drop_column("subscription_ends_at");batch.drop_column("exam_limit");batch.drop_column("student_limit");batch.drop_column("subscription_status");batch.drop_column("subscription_plan")
