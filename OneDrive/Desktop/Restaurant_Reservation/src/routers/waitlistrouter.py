from fastapi import FastAPI,HTTPException,APIRouter,Depends,Header
from database.database import SessionLocal
from src.models.waitlist import WaitlistDetails
from src.schemas.restaurantschemas import WaitlistData,WaitlistPatchData
import uuid
from datetime import datetime,timedelta
from src.utils.otp import generate_otp,send_otp_via_email
from src.utils.token import get_token,decode_token_password,decode_token_user_email,decode_token_user_id
from logs.log_config import logger



waitlists_log = APIRouter()
db = SessionLocal()

@waitlists_log.post("/waitlist_detail",response_model= WaitlistData)
def create_waitlist(waitlist: WaitlistData):
    # breakpoint()
    logger.info("enter waitlist detail")
    new_waitlist = WaitlistDetails(
        restaurant_id = waitlist.restaurant_id,
        user_id = waitlist.user_id,
        waitlist_time = waitlist.waitlist_time,
        number_of_guest = waitlist.number_of_guest,
        status = "waiting",
    )
    logger.info("add detail")
    db.add(new_waitlist)
    logger.info("commit waitlist detail")
    db.commit()
    logger.success("waitlist reservation added")
    return new_waitlist


@waitlists_log.get("/all_waitlist",response_model=list[ WaitlistData])
def read_waitlists():
    logger.info("check conditions")
    db_waitlist = db.query(WaitlistDetails).filter(WaitlistDetails.is_active == True,WaitlistDetails.is_deleted == False).all()
    if db_waitlist is None:
        logger.error("waitlist not found")
        raise HTTPException(status_code=404, detail="waitlists not found")
    logger.success("waitlist successfully got")
    return db_waitlist



@waitlists_log.get("/get_waitlist_id",response_model=WaitlistData)
def read_single_waitlist(waitlist_id: str):
    # user_id = decode_token_user_id(token)
    logger.info("check condtion and id")
    db_waitlist = db.query(WaitlistDetails).filter(WaitlistDetails.id == waitlist_id,WaitlistDetails.is_active == True,WaitlistDetails.is_deleted == False).first()
    
    if db_waitlist is None:
        logger.error("waitlist is not found")
        raise HTTPException(status_code=404, detail="waitlist not found")
    logger.success("waitlist detail get successfully")
    return db_waitlist



@waitlists_log.put("/update_waitlist_detail")
def update_waitlist_detail(waitlist: WaitlistData,waitlist_id: str):
    # user_id = decode_token_user_id(token)
    logger.info("check waitlist id and condition")
    db_waitlist = db.query(WaitlistDetails).filter(WaitlistDetails.id == waitlist_id).first()
    # breakpoint()
    if db_waitlist is None:
        logger.error("waitlist is not found")
        raise HTTPException(status_code=404, detail="waitlist detail not found")
    
    logger.info("status three of one")
    if db_waitlist.status not in ['waiting', 'notified', 'cancelled']:
        logger.error("invalid status")
        raise HTTPException(status_code=400, detail="Invalid status")
    
    logger.info("enter updated detail")
    db_waitlist.restaurant_id    = waitlist.restaurant_id,
    db_waitlist.user_id   = waitlist.user_id,
    db_waitlist.waitlist_time    = waitlist.waitlist_time,
    db_waitlist.number_of_guest = waitlist.number_of_guest,
    db_waitlist.status = waitlist.status,
    
    logger.info("commit detail")
    db.commit()
    logger.success("detail change successfully")
    return "your detail change succesfully"



@waitlists_log.patch("/update_waitlist")
def update_waitlist(waitlist: WaitlistPatchData,waitlist_id: str):
    # user_id = decode_token_user_id(token)
    logger.info("check waitlist id and condition")
    db_waitlist = db.query(WaitlistDetails).filter(WaitlistDetails.id == waitlist_id,WaitlistDetails.is_active == True).first()
    if db_waitlist is None:
        logger.error("waitlist is not found")
        raise HTTPException(status_code=404, detail="waitlist Not Found")
    update_data = waitlist.dict(exclude_unset=True)
    for key, value in update_data.items():
        logger.info("enter value of update detail")
        setattr(db_waitlist, key, value)
    logger.info("commit detail after changes")
    db.commit()
    db.refresh(db_waitlist)
    logger.success("detail change succesffuly")
    return {"message": "Details changed successfully", "User": db_waitlist}



@waitlists_log.delete("/delete_waitlist")
def delete_waitlist(waitlist_id: str):
    # user_id = decode_token_user_id(token)
    logger.info("check id and condition")
    db_waitlist = db.query(WaitlistDetails).filter(WaitlistDetails.id == waitlist_id,WaitlistDetails.is_active == True).first()
    if db_waitlist is None:
        logger.error("waitlist is not found")
        raise HTTPException(status_code=404, detail="waitlist is not found")
    logger.info("toggle boolean condition")
    db_waitlist.is_active  = False
    db_waitlist.is_deleted = True
    
    logger.info("commit delete detail")
    db.commit()
    logger.success("detail deleted successfully")
    return "you deleted successfully"
