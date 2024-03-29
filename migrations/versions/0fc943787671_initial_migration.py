"""initial migration

Revision ID: 0fc943787671
Revises: 
Create Date: 2022-08-26 16:48:10.317751

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0fc943787671'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('trials', sa.Column('ip_addy', sa.VARCHAR(length=80), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('trials', 'ip_addy')
    # ### end Alembic commands ###
