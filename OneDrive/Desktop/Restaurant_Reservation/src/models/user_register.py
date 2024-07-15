from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from datetime import datetime,timedelta,date,time
import uuid
from database.database import Base

class CustomerDetail(Base):
    __tablename__ = 'customer'
    id = Column(String(50), primary_key=True, default=str(uuid.uuid4()))
    uname = Column(String(50),nullable=False)
    email = Column(String(50),nullable=False)
    mobile_no = Column(String(15),nullable=False)
    gender = Column(String(10),nullable=False)
    password = Column(String(70),nullable=False)
    is_deleted = Column(Boolean,default=False)
    is_active = Column(Boolean,default=True)
    is_verified = Column(Boolean,default=False)
    created_at = Column(DateTime,default=datetime.now)
    modified_at = Column(DateTime,default=datetime.now,onupdate=datetime.now)
    