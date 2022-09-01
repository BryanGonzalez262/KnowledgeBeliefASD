"""empty message

Revision ID: 331668dcae09
Revises: 9b28d783fddb
Create Date: 2022-09-01 12:16:53.758335

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '331668dcae09'
down_revision = '9b28d783fddb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('unique_id',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('unique_code', sa.VARCHAR(length=20), nullable=True),
    sa.Column('used', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('unique_code')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('unique_id')
    # ### end Alembic commands ###
