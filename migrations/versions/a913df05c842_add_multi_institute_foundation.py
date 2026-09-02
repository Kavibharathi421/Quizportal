"""add multi institute foundation

Revision ID: a913df05c842
Revises: f18a63bc2901
"""
from alembic import op
import sqlalchemy as sa

revision="a913df05c842"
down_revision="f18a63bc2901"
branch_labels=None
depends_on=None

def upgrade():
    op.create_table("institutes",sa.Column("id",sa.Integer(),nullable=False),sa.Column("name",sa.String(length=160),nullable=False),sa.Column("slug",sa.String(length=80),nullable=False),sa.Column("status",sa.String(length=20),nullable=False),sa.Column("logo_url",sa.String(length=500)),sa.Column("primary_color",sa.String(length=20)),sa.Column("created_at",sa.DateTime(timezone=True)),sa.PrimaryKeyConstraint("id"),sa.UniqueConstraint("slug"))
    op.create_index("ix_institutes_slug","institutes",["slug"],unique=True)
    connection=op.get_bind();connection.execute(sa.text("INSERT INTO institutes (name,slug,status,primary_color,created_at) VALUES ('Axiom Learning Institute','axiom','ACTIVE','#4169e1',CURRENT_TIMESTAMP)"));institute_id=connection.execute(sa.text("SELECT id FROM institutes WHERE slug='axiom'")).scalar()
    for table in ("users","student_categories","exams"):
        with op.batch_alter_table(table) as batch:batch.add_column(sa.Column("institute_id",sa.Integer(),nullable=True))
        connection.execute(sa.text(f"UPDATE {table} SET institute_id=:institute_id"),{"institute_id":institute_id})
        with op.batch_alter_table(table) as batch:
            batch.alter_column("institute_id",existing_type=sa.Integer(),nullable=False);batch.create_foreign_key(f"fk_{table}_institute_id","institutes",["institute_id"],["id"]);batch.create_index(f"ix_{table}_institute_id",["institute_id"])

def downgrade():
    for table in ("exams","student_categories","users"):
        with op.batch_alter_table(table) as batch:batch.drop_index(f"ix_{table}_institute_id");batch.drop_constraint(f"fk_{table}_institute_id",type_="foreignkey");batch.drop_column("institute_id")
    op.drop_index("ix_institutes_slug",table_name="institutes");op.drop_table("institutes")
