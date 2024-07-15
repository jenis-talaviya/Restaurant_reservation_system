from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from datetime import datetime,timedelta,date,time
import uuid
from database.database import Base

class SpecialrequestsDetails(Base):
    __tablename__ = 'specialrequests'
    id = Column(String(50), primary_key=True, default=str(uuid.uuid4()))
    reservation_id = Column(String(50),ForeignKey('reservation.id'))
    status = Column(String(255),nullable=False,default='pending')
    request = Column(String(255),nullable=False)
    is_deleted = Column(Boolean,default=False)
    is_active = Column(Boolean,default=True)
    created_at = Column(DateTime,default=datetime.now)
    modified_at = Column(DateTime,default=datetime.now,onupdate=datetime.now)    