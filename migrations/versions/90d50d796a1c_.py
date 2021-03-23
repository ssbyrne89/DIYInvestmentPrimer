"""empty message

Revision ID: 90d50d796a1c
Revises: 
Create Date: 2021-03-18 09:34:43.181597

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '90d50d796a1c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('companies',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('Open_Price', sa.Float(), nullable=True),
    sa.Column('High', sa.Float(), nullable=True),
    sa.Column('Low', sa.Float(), nullable=True),
    sa.Column('Close_Price', sa.Float(), nullable=True),
    sa.Column('Adjusted_Close', sa.Float(), nullable=True),
    sa.Column('Volume', sa.Integer(), nullable=True),
    sa.Column('Dividend_Amount', sa.Float(), nullable=True),
    sa.Column('Year', sa.Integer(), nullable=True),
    sa.Column('Month', sa.Integer(), nullable=True),
    sa.Column('Company_Name', sa.String(length=128), nullable=True),
    sa.Column('Company_ticker', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('companies')
    # ### end Alembic commands ###