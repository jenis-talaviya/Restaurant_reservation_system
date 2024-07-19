from fastapi import FastAPI,HTTPException,APIRouter,Depends,Header
from database.database import SessionLocal
from src.models.specialrequest import SpecialrequestsDetails
from src.models.user_register import CustomerDetail
from src.schemas.restaurantschemas import SpecialrequestData,SpecialrequestPatchData
import uuid
from datetime import datetime,timedelta
from src.utils.otp import generate_otp,send_otp_via_email
from src.utils.token import get_token,decode_token_password,decode_token_user_email,decode_token_user_id
from src.utils.otp import send_email
from logs.log_config import logger


specialrequests_log = APIRouter()
db = SessionLocal()

@specialrequests_log.post("/specialrequest_detail",response_model= SpecialrequestData)
def create_specialrequest(specialrequest: SpecialrequestData):
    # breakpoint()
    logger.info("enter specialrequest")
    new_specialrequest = SpecialrequestsDetails(
        reservation_id =specialrequest.reservation_id,
        status ="pending",
        request =specialrequest.request,
    )
    logger.info("add specialrequest")
    db.add(new_specialrequest)
    logger.info("commit after adding detail")
    db.commit()
    logger.success("request added successfully")
    return new_specialrequest



@specialrequests_log.get("/all_specialrequest",response_model=list[ SpecialrequestData])
def read_specialrequests():
    logger.info(" check condition")
    db_specialrequest = db.query(SpecialrequestsDetails).filter(SpecialrequestsDetails.is_active == True,SpecialrequestsDetails.is_deleted == False).all()
    if db_specialrequest is None:
        logger.error("request not found")
        raise HTTPException(status_code=404, detail="specialrequest not found")
    logger.info("request get succesfully")
    return db_specialrequest



@specialrequests_log.get("/get_specialrequest_id",response_model=SpecialrequestData)
def read_single_specialrequest(specialrequest_id: str):
    # user_id = decode_token_user_id(token)
    logger.info("enter request id and check condition")
    db_specialrequest = db.query(SpecialrequestsDetails).filter(SpecialrequestsDetails.id == specialrequest_id,SpecialrequestsDetails.is_active == True,SpecialrequestsDetails.is_deleted == False).first()
    
    if db_specialrequest is None:
        logger.error("request detail not found")
        raise HTTPException(status_code=404, detail="specialrequest not found")
    logger.success("request detail get successfully")
    return db_specialrequest



@specialrequests_log.put("/accept_specialrequest")
def accept_specialrequest(request_id: str,):
    logger.info("enter request id and check condition")
    special_request = db.query(SpecialrequestsDetails).filter(SpecialrequestsDetails.id == request_id).first()
    if special_request is None:
        logger.error("request detail not found")
        raise HTTPException(status_code=404, detail="Special request not found")
    logger.info("status change")
    special_request.status = "accepted"
    logger.info("commit changes")
    db.commit()
    db.refresh(special_request)

    logger.info("check customer condition")
    user = db.query(CustomerDetail).filter(CustomerDetail.is_active == True,CustomerDetail.is_verified == False).first()
    if user is None:
        logger.error("user not available or not register")
        raise HTTPException(status_code=404, detail="User not found")
    
    logger.info("shend mail about accepted special request")
    user_email = user.email
    subject = "Your Special Request has been Accepted"
    body = f"Dear {user.uname},\n\nYour special request '{special_request.request}' has been accepted by the restaurant.\n\nThank you!"

    logger.info("check email accept and message")
    success, message = send_email(
        sender_email="jenistalaviya404@gmail.com",
        receiver_email=user_email,
        password="zghoimvlnpzerzkv",
        subject=subject,
        body=body
    )

    if not success:
        logger.error("email message not send")
        raise HTTPException(status_code=500, detail=message)

    logger.success("mail sent successfully")
    return {"message": "Special request accepted, email sent to user", "special_request": special_request}



@specialrequests_log.put("/update_specialrequest_detail")
def update_specialrequest_detail(specialrequests: SpecialrequestData,specialrequest_id: str):
    # user_id = decode_token_user_id(token)
    logger.info("enter request id and check condition")
    db_specialrequest = db.query(SpecialrequestsDetails).filter(SpecialrequestsDetails.id == specialrequest_id).first()
    # breakpoint()
    if db_specialrequest is None:
        logger.error("request detail not found")
        raise HTTPException(status_code=404, detail="specialrequest detail not found")
    
    logger.info("change detail")
    db_specialrequest.reservation_id    = specialrequests.reservation_id,
    db_specialrequest.request   = specialrequests.request,
    db_specialrequest.status    = specialrequests.status,

    logger.info("commit after adding detail")
    db.commit()
    logger.success("detail change successfully")
    return "your detail change succesfully"




@specialrequests_log.patch("/update_specialrequest")
def update_specialrequest(specialrequest: SpecialrequestPatchData,specialrequest_id: str):
    # user_id = decode_token_user_id(token)
    logger.info("enter request id and check condition")
    db_specialrequest = db.query(SpecialrequestsDetails).filter(SpecialrequestsDetails.id == specialrequest_id,SpecialrequestsDetails.is_active == True).first()
    if db_specialrequest is None:
        logger.error("request detail not found")
        raise HTTPException(status_code=404, detail="specialrequest Not Found")
    update_data = specialrequest.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_specialrequest, key, value)
    logger.info("commit after changing")
    db.commit()
    db.refresh(db_specialrequest)
    logger.success("change done successfully")
    return {"message": "Details changed successfully", "User": db_specialrequest}



@specialrequests_log.delete("/delete_specialrequest")
def delete_specialrequest(specialrequest_id: str):
    logger.info("enter request id and check condition")
    # user_id = decode_token_user_id(token)
    db_specialrequest = db.query(SpecialrequestsDetails).filter(SpecialrequestsDetails.id == specialrequest_id,SpecialrequestsDetails.is_active == True).first()
    if db_specialrequest is None:
        logger.error("request detail not found")
        raise HTTPException(status_code=404, detail="specialrequest is not found")
    logger.info("boolean value change")
    db_specialrequest.is_active  = False
    db_specialrequest.is_deleted = True

    logger.info("change commited")
    db.commit()
    logger.success("request deleted successfully")
    return "you deleted successfully"
