"""create restro reservation table

Revision ID: 0d328d686373
Revises: 54331f3d17ac
Create Date: 2024-07-08 11:11:56.613556

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0d328d686373'
down_revision: Union[str, None] = '54331f3d17ac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('restaurant',
    sa.Column('id', sa.String(length=50), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('address', sa.String(length=255), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('mobile_no', sa.String(length=10), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('review',
    sa.Column('id', sa.String(length=50), nullable=False),
    sa.Column('restaurant_id', sa.String(length=50), nullable=True),
    sa.Column('user_id', sa.String(length=50), nullable=True),
    sa.Column('rating', sa.String(length=100), nullable=False),
    sa.Column('comment', sa.String(length=255), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['restaurant_id'], ['restaurant.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['customer.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tables',
    sa.Column('id', sa.String(length=50), nullable=False),
    sa.Column('restaurant_id', sa.String(length=50), nullable=True),
    sa.Column('table_number', sa.String(length=10), nullable=False),
    sa.Column('capacity', sa.String(length=100), nullable=False),
    sa.Column('location_descripation', sa.String(length=255), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['restaurant_id'], ['restaurant.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('waitlist',
    sa.Column('id', sa.String(length=50), nullable=False),
    sa.Column('restaurant_id', sa.String(length=50), nullable=True),
    sa.Column('user_id', sa.String(length=50), nullable=True),
    sa.Column('waitlist_time', sa.DateTime(), nullable=False),
    sa.Column('number_of_guest', sa.String(length=255), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['restaurant_id'], ['restaurant.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['customer.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('reservation',
    sa.Column('id', sa.String(length=50), nullable=False),
    sa.Column('restaurant_id', sa.String(length=50), nullable=True),
    sa.Column('user_id', sa.String(length=50), nullable=True),
    sa.Column('table_id', sa.String(length=50), nullable=True),
    sa.Column('reservation_time', sa.DateTime(), nullable=False),
    sa.Column('number_of_guests', sa.String(length=100), nullable=False),
    sa.Column('status', sa.String(length=255), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['restaurant_id'], ['restaurant.id'], ),
    sa.ForeignKeyConstraint(['table_id'], ['tables.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['customer.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('specialrequests',
    sa.Column('id', sa.String(length=50), nullable=False),
    sa.Column('reservation_id', sa.String(length=50), nullable=True),
    sa.Column('status', sa.String(length=255), nullable=False),
    sa.Column('request', sa.String(length=255), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['reservation_id'], ['reservation.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('specialrequests')
    op.drop_table('reservation')
    op.drop_table('waitlist')
    op.drop_table('tables')
    op.drop_table('review')
    op.drop_table('restaurant')
    # ### end Alembic commands ###
