from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from datetime import datetime,timedelta,date,time
import uuid
from database.database import Base

class WaitlistDetails(Base):
    __tablename__ = 'waitlist'
    id = Column(String(50), primary_key=True, default=str(uuid.uuid4()))
    restaurant_id = Column(String(50),ForeignKey('restaurant.id'))
    user_id = Column(String(50),ForeignKey('customer.id'))
    waitlist_time = Column(DateTime,nullable=False)
    number_of_guest = Column(String(255),nullable=False)
    status = Column(String(20),nullable=False)
    is_deleted = Column(Boolean,default=False)
    is_active = Column(Boolean,default=True)
    created_at = Column(DateTime,default=datetime.now)
    modified_at = Column(DateTime,default=datetime.now,onupdate=datetime.now)    