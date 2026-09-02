"""add account security tokens

Revision ID: f18a63bc2901
Revises: e73c1ad94120
"""
from alembic import op
import sqlalchemy as sa

revision="f18a63bc2901"
down_revision="e73c1ad94120"
branch_labels=None
depends_on=None

def upgrade():
    with op.batch_alter_table("users") as batch:
        batch.add_column(sa.Column("email_verified",sa.Boolean(),nullable=False,server_default=sa.true()))
    op.create_table("account_tokens",
        sa.Column("id",sa.Integer(),nullable=False),sa.Column("user_id",sa.Integer(),nullable=False),
        sa.Column("purpose",sa.String(length=30),nullable=False),sa.Column("token_hash",sa.String(length=64),nullable=False),
        sa.Column("expires_at",sa.DateTime(timezone=True),nullable=False),sa.Column("used_at",sa.DateTime(timezone=True)),sa.Column("created_at",sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(["user_id"],["users.id"]),sa.PrimaryKeyConstraint("id"),sa.UniqueConstraint("token_hash"))
    op.create_index("ix_account_tokens_user_id","account_tokens",["user_id"])
    op.create_index("ix_account_tokens_purpose","account_tokens",["purpose"])
    op.create_index("ix_account_tokens_token_hash","account_tokens",["token_hash"],unique=True)

def downgrade():
    op.drop_index("ix_account_tokens_token_hash",table_name="account_tokens");op.drop_index("ix_account_tokens_purpose",table_name="account_tokens");op.drop_index("ix_account_tokens_user_id",table_name="account_tokens");op.drop_table("account_tokens")
    with op.batch_alter_table("users") as batch:batch.drop_column("email_verified")
