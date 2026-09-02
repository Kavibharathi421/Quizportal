"""scope category names to institute

Revision ID: b742ed5a1c63
Revises: a913df05c842
"""
from alembic import op

revision="b742ed5a1c63"
down_revision="a913df05c842"
branch_labels=None
depends_on=None

def upgrade():
    with op.batch_alter_table("student_categories") as batch:
        batch.drop_constraint("name",type_="unique")
        batch.create_unique_constraint("uq_institute_category_name",["institute_id","name"])

def downgrade():
    with op.batch_alter_table("student_categories") as batch:
        batch.drop_constraint("uq_institute_category_name",type_="unique")
        batch.create_unique_constraint("name",["name"])
