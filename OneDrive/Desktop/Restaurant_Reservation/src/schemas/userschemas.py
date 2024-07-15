from pydantic import BaseModel
from typing import Optional
from datetime import date,time,datetime

class UserData(BaseModel):
    uname    : str
    email    : str
    mobile_no : str
    gender   : str
    password : str
    
    
class OtpRequest(BaseModel):
    email :str
    
    
class Otpverify(BaseModel):
    email : str
    otp   : str
    

class CustomerPatch(BaseModel):
    uname    : Optional[str] = None
    email    : Optional[str] = None
    mobile_no : Optional[str] = None
    gender   : Optional[str] = None
    password : Optional[str] = None