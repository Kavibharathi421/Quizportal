"""add unique exam access codes

Revision ID: a42b8e91c301
Revises: d31fa8ce742b
"""
from alembic import op
import sqlalchemy as sa
import secrets

revision = "a42b8e91c301"
down_revision = "d31fa8ce742b"
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table("exams") as batch_op:
        batch_op.add_column(sa.Column("access_code",sa.String(length=10),nullable=True))
    connection=op.get_bind()
    exam_ids=[row[0] for row in connection.execute(sa.text("SELECT id FROM exams"))]
    used=set()
    for exam_id in exam_ids:
        code=secrets.token_hex(5).upper()
        while code in used:code=secrets.token_hex(5).upper()
        used.add(code);connection.execute(sa.text("UPDATE exams SET access_code=:code WHERE id=:id"),{"code":code,"id":exam_id})
    with op.batch_alter_table("exams") as batch_op:
        batch_op.alter_column("access_code",existing_type=sa.String(length=10),nullable=False)
        batch_op.create_index("ix_exams_access_code",["access_code"],unique=True)

def downgrade():
    with op.batch_alter_table("exams") as batch_op:
        batch_op.drop_index("ix_exams_access_code")
        batch_op.drop_column("access_code")
