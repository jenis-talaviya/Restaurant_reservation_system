from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from datetime import datetime,timedelta,date,time
import uuid
from database.database import Base

class ReviewDetails(Base):
    __tablename__ = 'review'
    id = Column(String(50), primary_key=True, default=str(uuid.uuid4()))
    restaurant_id = Column(String(50),ForeignKey('restaurant.id'))
    user_id = Column(String(50),ForeignKey('customer.id'))
    rating = Column(String(100),nullable=False)
    comment = Column(String(255),nullable=False)
    is_deleted = Column(Boolean,default=False)
    is_active = Column(Boolean,default=True)
    created_at = Column(DateTime,default=datetime.now)
    modified_at = Column(DateTime,default=datetime.now,onupdate=datetime.now)    