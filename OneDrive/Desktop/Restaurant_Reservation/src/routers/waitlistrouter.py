from fastapi import FastAPI,HTTPException,APIRouter,Depends,Header
from database.database import SessionLocal
from src.models.waitlist import WaitlistDetails
from src.schemas.restaurantschemas import WaitlistData,WaitlistPatchData
import uuid
from datetime import datetime,timedelta
from src.utils.otp import generate_otp,send_otp_via_email
from src.utils.token import get_token,decode_token_password,decode_token_user_email,decode_token_user_id



waitlists_log = APIRouter()
db = SessionLocal()

@waitlists_log.post("/waitlist_detail",response_model= WaitlistData)
def create_waitlist(waitlist: WaitlistData):
    # breakpoint()
        
    new_waitlist = WaitlistDetails(
        restaurant_id = waitlist.restaurant_id,
        user_id = waitlist.user_id,
        waitlist_time = waitlist.waitlist_time,
        number_of_guest = waitlist.number_of_guest,
        status = "waiting",
    )
    db.add(new_waitlist)
    db.commit()
    return new_waitlist


@waitlists_log.get("/all_waitlist",response_model=list[ WaitlistData])
def read_waitlists():
    db_waitlist = db.query(WaitlistDetails).filter(WaitlistDetails.is_active == True,WaitlistDetails.is_deleted == False).all()
    if db_waitlist is None:
        raise HTTPException(status_code=404, detail="waitlists not found")
    return db_waitlist



@waitlists_log.get("/get_waitlist_id",response_model=WaitlistData)
def read_single_waitlist(waitlist_id: str):
    # user_id = decode_token_user_id(token)
    db_waitlist = db.query(WaitlistDetails).filter(WaitlistDetails.id == waitlist_id,WaitlistDetails.is_active == True,WaitlistDetails.is_deleted == False).first()
    
    if db_waitlist is None:
        raise HTTPException(status_code=404, detail="waitlist not found")
    return db_waitlist



@waitlists_log.put("/update_waitlist_detail")
def update_waitlist_detail(waitlist: WaitlistData,waitlist_id: str):
    # user_id = decode_token_user_id(token)
    
    db_waitlist = db.query(WaitlistDetails).filter(WaitlistDetails.id == waitlist_id).first()
    # breakpoint()
    if db_waitlist is None:
        raise HTTPException(status_code=404, detail="waitlist detail not found")
    
    if db_waitlist.status not in ['waiting', 'notified', 'cancelled']:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    db_waitlist.restaurant_id    = waitlist.restaurant_id,
    db_waitlist.user_id   = waitlist.user_id,
    db_waitlist.waitlist_time    = waitlist.waitlist_time,
    db_waitlist.number_of_guest = waitlist.number_of_guest,
    db_waitlist.status = waitlist.status,
    
    db.commit()
    return "your detail change succesfully"



@waitlists_log.patch("/update_waitlist")
def update_waitlist(waitlist: WaitlistPatchData,waitlist_id: str):
    # user_id = decode_token_user_id(token)
    db_waitlist = db.query(WaitlistDetails).filter(WaitlistDetails.id == waitlist_id,WaitlistDetails.is_active == True).first()
    if db_waitlist is None:
        raise HTTPException(status_code=404, detail="waitlist Not Found")
    update_data = waitlist.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_waitlist, key, value)
    db.commit()
    db.refresh(db_waitlist)
    return {"message": "Details changed successfully", "User": db_waitlist}



@waitlists_log.delete("/delete_waitlist")
def delete_waitlist(waitlist_id: str):
    # user_id = decode_token_user_id(token)
    db_waitlist = db.query(WaitlistDetails).filter(WaitlistDetails.id == waitlist_id,WaitlistDetails.is_active == True).first()
    if db_waitlist is None:
        raise HTTPException(status_code=404, detail="waitlist is not found")
    db_waitlist.is_active  = False
    db_waitlist.is_deleted = True
    
    db.commit()
    return "you deleted successfully"
