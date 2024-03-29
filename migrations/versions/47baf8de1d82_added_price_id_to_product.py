"""Added price_id to Product

Revision ID: 47baf8de1d82
Revises: 4821e8e577fc
Create Date: 2024-02-09 17:13:17.483783

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '47baf8de1d82'
down_revision = '4821e8e577fc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.add_column(sa.Column('price_id', sa.String(length=100), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.drop_column('price_id')

    # ### end Alembic commands ###
