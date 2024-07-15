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


specialrequests_log = APIRouter()
db = SessionLocal()

@specialrequests_log.post("/specialrequest_detail",response_model= SpecialrequestData)
def create_specialrequest(specialrequest: SpecialrequestData):
    # breakpoint()
        
    new_specialrequest = SpecialrequestsDetails(
        reservation_id =specialrequest.reservation_id,
        status ="pending",
        request =specialrequest.request,
    )
    db.add(new_specialrequest)
    db.commit()
    return new_specialrequest



@specialrequests_log.get("/all_specialrequest",response_model=list[ SpecialrequestData])
def read_specialrequests():
    db_specialrequest = db.query(SpecialrequestsDetails).filter(SpecialrequestsDetails.is_active == True,SpecialrequestsDetails.is_deleted == False).all()
    if db_specialrequest is None:
        raise HTTPException(status_code=404, detail="specialrequest not found")
    return db_specialrequest



@specialrequests_log.get("/get_specialrequest_id",response_model=SpecialrequestData)
def read_single_specialrequest(specialrequest_id: str):
    # user_id = decode_token_user_id(token)
    db_specialrequest = db.query(SpecialrequestsDetails).filter(SpecialrequestsDetails.id == specialrequest_id,SpecialrequestsDetails.is_active == True,SpecialrequestsDetails.is_deleted == False).first()
    
    if db_specialrequest is None:
        raise HTTPException(status_code=404, detail="specialrequest not found")
    return db_specialrequest



@specialrequests_log.put("/accept_specialrequest")
def accept_specialrequest(request_id: str,):
    special_request = db.query(SpecialrequestsDetails).filter(SpecialrequestsDetails.id == request_id).first()
    if special_request is None:
        raise HTTPException(status_code=404, detail="Special request not found")

    special_request.status = "accepted"
    db.commit()
    db.refresh(special_request)

    user = db.query(CustomerDetail).filter(CustomerDetail.is_active == True,CustomerDetail.is_verified == False).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user_email = user.email
    subject = "Your Special Request has been Accepted"
    body = f"Dear {user.uname},\n\nYour special request '{special_request.request}' has been accepted by the restaurant.\n\nThank you!"

    success, message = send_email(
        sender_email="jenistalaviya404@gmail.com",
        receiver_email=user_email,
        password="zghoimvlnpzerzkv",
        subject=subject,
        body=body
    )

    if not success:
        raise HTTPException(status_code=500, detail=message)

    return {"message": "Special request accepted, email sent to user", "special_request": special_request}



@specialrequests_log.put("/update_specialrequest_detail")
def update_specialrequest_detail(specialrequests: SpecialrequestData,specialrequest_id: str):
    # user_id = decode_token_user_id(token)
    
    db_specialrequest = db.query(SpecialrequestsDetails).filter(SpecialrequestsDetails.id == specialrequest_id).first()
    # breakpoint()
    if db_specialrequest is None:
        raise HTTPException(status_code=404, detail="specialrequest detail not found")
    
    db_specialrequest.reservation_id    = specialrequests.reservation_id,
    db_specialrequest.request   = specialrequests.request,
    db_specialrequest.status    = specialrequests.status,

    
    db.commit()
    return "your detail change succesfully"




@specialrequests_log.patch("/update_specialrequest")
def update_specialrequest(specialrequest: SpecialrequestPatchData,specialrequest_id: str):
    # user_id = decode_token_user_id(token)
    db_specialrequest = db.query(SpecialrequestsDetails).filter(SpecialrequestsDetails.id == specialrequest_id,SpecialrequestsDetails.is_active == True).first()
    if db_specialrequest is None:
        raise HTTPException(status_code=404, detail="specialrequest Not Found")
    update_data = specialrequest.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_specialrequest, key, value)
    db.commit()
    db.refresh(db_specialrequest)
    return {"message": "Details changed successfully", "User": db_specialrequest}



@specialrequests_log.delete("/delete_specialrequest")
def delete_specialrequest(specialrequest_id: str):
    # user_id = decode_token_user_id(token)
    db_specialrequest = db.query(SpecialrequestsDetails).filter(SpecialrequestsDetails.id == specialrequest_id,SpecialrequestsDetails.is_active == True).first()
    if db_specialrequest is None:
        raise HTTPException(status_code=404, detail="specialrequest is not found")
    db_specialrequest.is_active  = False
    db_specialrequest.is_deleted = True
    
    db.commit()
    return "you deleted successfully"
