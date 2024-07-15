from fastapi import FastAPI,HTTPException,APIRouter,Depends,Header
from database.database import SessionLocal
from src.models.user_register import CustomerDetail
from src.models.user_verify import OTPDetail
from src.schemas.userschemas import UserData,OtpRequest,Otpverify,CustomerPatch
import uuid
from datetime import datetime,timedelta
from passlib.context import CryptContext
from src.utils.otp import generate_otp,send_otp_via_email
from src.utils.token import get_token,decode_token_password,decode_token_user_email,decode_token_user_id



customer_log = APIRouter()
db = SessionLocal()

pwd_context = CryptContext(schemes=["bcrypt"],deprecated = "auto")

@customer_log.post("/customer_register",response_model=UserData)
def create_user(use:UserData):
    # breakpoint()
    
    if not use.mobile_no.isdigit() or len(use.mobile_no) != 10:
        raise HTTPException(status_code=400, detail="Mobile number must be exactly 10 digits")
    
    db_user = db.query(CustomerDetail).filter(CustomerDetail.uname == use.uname).first()
    if db_user is not None:
        raise HTTPException(status_code=404, detail="same user name already available")
    
    db_user = db.query(CustomerDetail).filter(CustomerDetail.email == use.email).first()
    if db_user is not None:
        raise HTTPException(status_code=404, detail="same user email already available")
    
    db_user = db.query(CustomerDetail).filter(CustomerDetail.mobile_no == use.mobile_no).first()
    if db_user is not None:
        raise HTTPException(status_code=404, detail="same mobileno. already available")
    
    new_user = CustomerDetail(
        uname = use.uname,
        email = use.email,
        mobile_no = use.mobile_no,
        gender = use.gender,
        password = pwd_context.hash(use.password)
    )
    db.add(new_user)
    db.commit()
    return new_user


@customer_log.get("/all_customer",response_model=list[UserData])
def read_users():
    db_user = db.query(CustomerDetail).filter(CustomerDetail.is_active == True,CustomerDetail.is_deleted == False,CustomerDetail.is_verified == True).all()
    if db_user is None:
        raise HTTPException(status_code=404, detail="users not found")
    return db_user



@customer_log.get("/get_customer_id",response_model=UserData)
def read_single_users(token: str):
    user_id = decode_token_user_id(token)
    db_user = db.query(CustomerDetail).filter(CustomerDetail.id == user_id,CustomerDetail.is_active == True,CustomerDetail.is_deleted == False,CustomerDetail.is_verified == True).first()
    
    if db_user is None:
        raise HTTPException(status_code=404, detail="user not found")
    return db_user



@customer_log.put("/update_customer")
def update_user_detail(users: UserData,token: str):
    user_id = decode_token_user_id(token)
    
    db_user = db.query(CustomerDetail).filter(CustomerDetail.uname == users.uname).first()
    if db_user is not None and CustomerDetail.uname == users.uname:
        raise HTTPException(status_code=404, detail="same user name already available")
    
    db_user = db.query(CustomerDetail).filter(CustomerDetail.email == users.email).first()
    if db_user is not None and CustomerDetail.email == users.email:
        raise HTTPException(status_code=404, detail="same user email already available")
    
    db_user = db.query(CustomerDetail).filter(CustomerDetail.mobile_no == users.mobile_no).first()
    if db_user is not None and CustomerDetail.mobile_no == users.mobile_no:
        raise HTTPException(status_code=404, detail="same user mobileno. already available")
    
    db_user = db.query(CustomerDetail).filter(CustomerDetail.id == user_id,CustomerDetail.is_active == True,CustomerDetail.is_deleted == False,CustomerDetail.is_verified == True).first()
    # breakpoint()
    if db_user is None:
        raise HTTPException(status_code=404, detail="users detail not found")
    
    db_user.uname    = users.uname,
    db_user.email    = users.email,
    db_user.mobile_no= users.mobile_no,
    db_user.gender   = users.gender
    
    db.commit()
    return "your detail change succesfully"



@customer_log.patch("/update_data")
def update_data(Customerdetails: CustomerPatch,token: str):
    user_id = decode_token_user_id(token)
    db_user = db.query(CustomerDetail).filter(CustomerDetail.id == user_id,CustomerDetail.is_active == True,CustomerDetail.is_verified == True).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User Not Found")
    update_data = Customerdetails.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return {"message": "Details changed successfully", "User": db_user}



@customer_log.delete("/delete_customer")
def delete_user(token: str):
    user_id = decode_token_user_id(token)
    db_user = db.query(CustomerDetail).filter(CustomerDetail.id == user_id,CustomerDetail.is_active == True).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="users is not found")
    db_user.is_active  = False
    db_user.is_deleted = True
    db_user.is_verified = False
    
    db.commit()
    return "you deleted successfully"


#---------------------------------------------------------OTP Section------------------------------------------------------------

otp_verify = APIRouter()
db = SessionLocal()


@otp_verify.post("/generate_otp")
def generate_otp_for_user(email: str):
    db_user = db.query(CustomerDetail).filter(CustomerDetail.email == email, CustomerDetail.is_active == True).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="email is not registered")
    
    otp_code = generate_otp()
    expiry_time = datetime.now() + timedelta(minutes=10)  # OTP valid for 10 minutes
    new_otp = OTPDetail(
        email=email,
        otp=otp_code,
        expiry_time=expiry_time
    )
    db.add(new_otp)
    db.commit()

    # Send OTP via email
    sender_email = "jenistalaviya404@gmail.com"
    receiver_email = email
    email_password = "zghoimvlnpzerzkv"
    success, message = send_otp_via_email(sender_email, receiver_email, email_password, otp_code)

    if not success:
        raise HTTPException(status_code=500, detail="otp can't sent")

    return {"message": "OTP sent to email", "email": email}



@otp_verify.post("/verify_otp")
def verify_otp(email: str, otp: str):
    db_record = db.query(OTPDetail).filter(OTPDetail.email == email, OTPDetail.otp == otp).first()
    if not db_record:
        raise HTTPException(status_code=400, detail="Invalid Entered OTP")
    
    # Check if the OTP has expired
    if datetime.now() > db_record.expiry_time:
        raise HTTPException(status_code=400, detail="OTP Time expired")
    
    user_record = db.query(CustomerDetail).filter(CustomerDetail.email == email).first()
    if not user_record:
        raise HTTPException(status_code=400, detail="Email is not found")
    
    # Update the is_verified field in the USERDetail table
    user_record.is_verified = True
    
    db.delete(db_record)
    db.commit()
    return {"message": "OTP verified successfully"}


@otp_verify.get("/logging_users")
def logging_user(email:str, password:str):
    db_user = db.query(CustomerDetail).filter(CustomerDetail.email == email,CustomerDetail.is_active == True,CustomerDetail.is_deleted == False,CustomerDetail.is_verified == True).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="user is not found")
    
    if not pwd_context.verify(password,db_user.password):
        raise HTTPException(status_code=404, detail="password is incorrect")
        
    access_token = get_token(db_user.id,email,password)
    return access_token




@otp_verify.put("/reset_password")
def reset_password(newpass: str,token: str):
    user_id = decode_token_user_id(token)
    email   = decode_token_user_email(token)
    password= decode_token_password(token)
    db_user = db.query(CustomerDetail).filter(CustomerDetail.id == user_id,CustomerDetail.email == email,CustomerDetail.is_active == True).first()
    if db_user is None:
        raise HTTPException("user data is not found")
    
    if pwd_context.verify(password,db_user.password):
        db_user.password = pwd_context.hash(newpass)
        db.commit()
        return "password reset successfully"
    else:
        return "old password is not match"
    
    
    
@otp_verify.put("/reregister_user")
def update_user_pass(email: str, password: str,token: str):
    # breakpoint()
    user_id = decode_token_user_id(token)
    db_user = db.query(CustomerDetail).filter(CustomerDetail.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="user not found")
    
    if db_user.is_active == False and db_user.is_deleted == True:
        if pwd_context.verify(password,db_user.password):
            db_user.is_active = True
            db_user.is_deleted = False
            db.commit()
            return "you successfully Reregister"
    else:
        raise HTTPException(status_code=404, detail="email or password is not match")
    
    

@otp_verify.put("/forget_password")
def forget_password(user_newpass: str,token: str):
    user_id = decode_token_user_id(token)
    db_user = db.query(CustomerDetail).filter(CustomerDetail.id == user_id, CustomerDetail.is_active == True, CustomerDetail.is_verified == True, CustomerDetail.is_deleted == False).first()
    
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not db_user.is_verified:
        return "User not verified"
    
    db_user.password = pwd_context.hash(user_newpass)
    db.commit()
    return "Forget Password successfully"