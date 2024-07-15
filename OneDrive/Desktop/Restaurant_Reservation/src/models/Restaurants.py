from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from datetime import datetime,timedelta,date,time
import uuid
from database.database import Base

class RestaurantDetail(Base):
    __tablename__ = 'restaurant'
    id = Column(String(50), primary_key=True, default=str(uuid.uuid4()))
    name = Column(String(50),nullable=False)
    cuisine_type = Column(String(50),nullable=False)
    address = Column(String(255),nullable=False)
    email = Column(String(100),nullable=False)
    mobile_no = Column(String(10),nullable=False)
    opening_hours = Column(String(100),nullable=False)
    is_deleted = Column(Boolean,default=False)
    average_cost = Column(String(100),nullable=False)
    is_active = Column(Boolean,default=True)
    created_at = Column(DateTime,default=datetime.now)
    modified_at = Column(DateTime,default=datetime.now,onupdate=datetime.now)
    