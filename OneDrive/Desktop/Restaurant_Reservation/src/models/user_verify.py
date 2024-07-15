from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from datetime import datetime,timedelta,date,time
import uuid
from database.database import Base

class OTPDetail(Base):
    __tablename__ = 'otp_details'
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(50), nullable=False)
    otp = Column(String(6), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    expiry_time = Column(DateTime,default=lambda: datetime.now() + timedelta(minutes=10))
    