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
from logs.log_config import logger



customer_log = APIRouter()
db = SessionLocal()

pwd_context = CryptContext(schemes=["bcrypt"],deprecated = "auto")

@customer_log.post("/customer_register",response_model=UserData)
def create_user(use:UserData):
    # breakpoint()
    logger.info("check mobile number should be 10 digit")
    if not use.mobile_no.isdigit() or len(use.mobile_no) != 10:
        raise HTTPException(status_code=400, detail="Mobile number must be exactly 10 digits")
    
    logger.info("uname already register or not")
    db_user = db.query(CustomerDetail).filter(CustomerDetail.uname == use.uname).first()
    if db_user is not None:
        raise HTTPException(status_code=404, detail="same user name already available")
    
    logger.info("email already register or not")    
    db_user = db.query(CustomerDetail).filter(CustomerDetail.email == use.email).first()
    if db_user is not None:
        raise HTTPException(status_code=404, detail="same user email already available")
    
    logger.info("mobile no already register or not")    
    db_user = db.query(CustomerDetail).filter(CustomerDetail.mobile_no == use.mobile_no).first()
    if db_user is not None:
        raise HTTPException(status_code=404, detail="same mobileno. already available")
    
    logger.info("enter user detail")    
    new_user = CustomerDetail(
        uname = use.uname,
        email = use.email,
        mobile_no = use.mobile_no,
        gender = use.gender,
        password = pwd_context.hash(use.password)
    )
    logger.info("add detail in database")
    db.add(new_user)
    logger.info("commit enter detail")
    db.commit()
    logger.success("user register successfully")
    return new_user


@customer_log.get("/all_customer",response_model=list[UserData])
def read_users():
    logger.info("check codition true or not")
    db_user = db.query(CustomerDetail).filter(CustomerDetail.is_active == True,CustomerDetail.is_deleted == False,CustomerDetail.is_verified == True).all()
    if db_user is None:
        logger.error("user not found")
        raise HTTPException(status_code=404, detail="users not found")
    logger.success("customers detail found it")
    return db_user



@customer_log.get("/get_customer_id",response_model=UserData)
def read_single_users(token: str):
    logger.info("enter user_id using token")
    user_id = decode_token_user_id(token)
    logger.info("check user register or not")
    db_user = db.query(CustomerDetail).filter(CustomerDetail.id == user_id,CustomerDetail.is_active == True,CustomerDetail.is_deleted == False,CustomerDetail.is_verified == True).first()
    
    if db_user is None:
        logger.error("user_id not found")
        raise HTTPException(status_code=404, detail="user not found")
    logger.success("customer detail found successfully")
    return db_user



@customer_log.put("/update_customer")
def update_user_detail(users: UserData,token: str):
    logger.info("enter user_id using token")
    user_id = decode_token_user_id(token)
    
    logger.info("uname already register or not")
    db_user = db.query(CustomerDetail).filter(CustomerDetail.uname == users.uname).first()
    if db_user is not None and CustomerDetail.uname == users.uname:
        raise HTTPException(status_code=404, detail="same user name already available")
    
    logger.info("email already register or not")
    db_user = db.query(CustomerDetail).filter(CustomerDetail.email == users.email).first()
    if db_user is not None and CustomerDetail.email == users.email:
        raise HTTPException(status_code=404, detail="same user email already available")
    
    logger.info("mobile no already register or not")
    db_user = db.query(CustomerDetail).filter(CustomerDetail.mobile_no == users.mobile_no).first()
    if db_user is not None and CustomerDetail.mobile_no == users.mobile_no:
        raise HTTPException(status_code=404, detail="same user mobileno. already available")
    
    logger.info("customer available or not")
    db_user = db.query(CustomerDetail).filter(CustomerDetail.id == user_id,CustomerDetail.is_active == True,CustomerDetail.is_deleted == False,CustomerDetail.is_verified == True).first()
    # breakpoint()
    if db_user is None:
        logger.error("user not available")
        raise HTTPException(status_code=404, detail="users detail not found")
    
    logger.info("enter detail for changes")
    db_user.uname    = users.uname,
    db_user.email    = users.email,
    db_user.mobile_no= users.mobile_no,
    db_user.gender   = users.gender
    
    logger.info("commit after detail change")
    db.commit()
    logger.success("detail change successfully")
    return "your detail change succesfully"



@customer_log.patch("/update_data")
def update_data(Customerdetails: CustomerPatch,token: str):
    logger.info("enter user_id using token")
    user_id = decode_token_user_id(token)
    logger.info("customer available or not with checking condition")
    db_user = db.query(CustomerDetail).filter(CustomerDetail.id == user_id,CustomerDetail.is_active == True,CustomerDetail.is_verified == True).first()
    if db_user is None:
        logger.error("customer id not found")
        raise HTTPException(status_code=404, detail="User Not Found")
    update_data = Customerdetails.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    logger.info("commit after change detail")
    db.commit()
    db.refresh(db_user)
    logger.success("detail save successfully after doing changes")
    return {"message": "Details changed successfully", "User": db_user}



@customer_log.delete("/delete_customer")
def delete_user(token: str):
    logger.info("enter user_id using token")
    user_id = decode_token_user_id(token)
    logger.info("customer available or not with checking condition")
    db_user = db.query(CustomerDetail).filter(CustomerDetail.id == user_id,CustomerDetail.is_active == True).first()
    if db_user is None:
        logger.error("custmore id not found")
        raise HTTPException(status_code=404, detail="users is not found")
    
    logger.info("toggle true and false value")
    db_user.is_active  = False
    db_user.is_deleted = True
    db_user.is_verified = False
    
    logger.info("commit detail after doing changes")
    db.commit()
    logger.success("user detail successfully")
    return "you deleted successfully"


#---------------------------------------------------------OTP Section------------------------------------------------------------

otp_verify = APIRouter()
db = SessionLocal()


@otp_verify.post("/generate_otp")
def generate_otp_for_user(email: str):
    logger.info("enter email and check si active or not")
    db_user = db.query(CustomerDetail).filter(CustomerDetail.email == email, CustomerDetail.is_active == True).first()
    if not db_user:
        logger.error("email is not registered")
        raise HTTPException(status_code=404, detail="email is not registered")
    
    logger.info("generate otp after conditon is true")
    otp_code = generate_otp()
    expiry_time = datetime.now() + timedelta(minutes=10)  # OTP valid for 10 minutes
    new_otp = OTPDetail(
        email=email,
        otp=otp_code,
        expiry_time=expiry_time
    )
    logger.info("add otp for register email")
    db.add(new_otp)
    logger.info("commit otp")
    db.commit()

    logger.info("send otp via email")
    # Send OTP via email
    sender_email = "youremail@gmail.com"
    receiver_email = email
    email_password = "yourpassword"
    success, message = send_otp_via_email(sender_email, receiver_email, email_password, otp_code)

    if not success:
        logger.error("otp can't sent to email")
        raise HTTPException(status_code=500, detail="otp can't sent")

    logger.success("otp sent successfully")
    return {"message": "OTP sent to email", "email": email}



@otp_verify.post("/verify_otp")
def verify_otp(email: str, otp: str):
    logger.info("enter email and otp after check true")
    db_record = db.query(OTPDetail).filter(OTPDetail.email == email, OTPDetail.otp == otp).first()
    if not db_record:
        logger.error("otp enter is wrong")
        raise HTTPException(status_code=400, detail="Invalid Entered OTP")
    
    logger.info("check otp has expire or not")
    # Check if the OTP has expired
    if datetime.now() > db_record.expiry_time:
        logger.error("otp time expired")
        raise HTTPException(status_code=400, detail="OTP Time expired")
    
    logger.info("email available or not")
    user_record = db.query(CustomerDetail).filter(CustomerDetail.email == email).first()
    if not user_record:
        logger.error("email is not found")
        raise HTTPException(status_code=400, detail="Email is not found")
    
    # Update the is_verified field in the USERDetail table
    logger.info("update is verified in userdetail table")
    user_record.is_verified = True
    
    logger.info("delete otp after using")
    db.delete(db_record)
    logger.info("commit after using it")
    db.commit()
    logger.success("otp verified successfully")
    return {"message": "OTP verified successfully"}


@otp_verify.get("/logging_users")
def logging_user(email:str, password:str):
    logger.info("enter email and password and check conditions")
    db_user = db.query(CustomerDetail).filter(CustomerDetail.email == email,CustomerDetail.is_active == True,CustomerDetail.is_deleted == False,CustomerDetail.is_verified == True).first()
    if db_user is None:
        logger.error("user email not found")
        raise HTTPException(status_code=404, detail="user is not found")
    
    if not pwd_context.verify(password,db_user.password):
        logger.error("password incorrect")
        raise HTTPException(status_code=404, detail="password is incorrect")
        
    access_token = get_token(db_user.id,email,password)
    logger.success("token getting successfully")
    return access_token




@otp_verify.put("/reset_password")
def reset_password(newpass: str,token: str):
    logger.info("decode user_id,email,password from token")
    user_id = decode_token_user_id(token)
    email   = decode_token_user_email(token)
    password= decode_token_password(token)
    logger.info("check email and user id register or not")
    db_user = db.query(CustomerDetail).filter(CustomerDetail.id == user_id,CustomerDetail.email == email,CustomerDetail.is_active == True).first()
    if db_user is None:
        logger.error("user id or user not register")
        raise HTTPException("user data is not found")
    
    logger.info("verify password with customer detail table same or not")
    if pwd_context.verify(password,db_user.password):
        db_user.password = pwd_context.hash(newpass)
        logger.info("after reset password commit it")
        db.commit()
        logger.success("password reset successfully")
        return "password reset successfully"
    else:
        logger.error("your password is mismatch")
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
    logger.info("take user id with using token")
    user_id = decode_token_user_id(token)
    logger.info("check condition of user which satisfy or not")
    db_user = db.query(CustomerDetail).filter(CustomerDetail.id == user_id, CustomerDetail.is_active == True, CustomerDetail.is_verified == True, CustomerDetail.is_deleted == False).first()
    
    if db_user is None:
        logger.error("user not found")
        raise HTTPException(status_code=404, detail="User not found")
    
    logger.info("check user is verified or not")
    if not db_user.is_verified:
        logger.error("user is not verified")
        return "User not verified"
    
    logger.info("enter new password")
    db_user.password = pwd_context.hash(user_newpass)
    logger.info("after enter password commit")
    db.commit()
    logger.success("password forgot change successfully")
    return "Forget Password successfully"