from fastapi import FastAPI,HTTPException,APIRouter,Depends,Header
from database.database import SessionLocal
from src.models.reservations import ResrvationsDetails
from src.schemas.restaurantschemas import ReservationData,ReservationPatchData
from src.models.user_register import CustomerDetail
from src.models.table import TableDetails
import uuid
from datetime import datetime,timedelta
from src.utils.otp import send_email



reserve_log = APIRouter()
db = SessionLocal()

@reserve_log.post("/reservation_detail",response_model=ReservationData)
def create_user(resrves:ReservationData):
    # breakpoint()
    
    existing_reservation = db.query(ResrvationsDetails).filter(ResrvationsDetails.table_id == resrves.table_id,ResrvationsDetails.reservation_time == resrves.reservation_time,ResrvationsDetails.is_active == True,ResrvationsDetails.is_deleted == False).first()
    
    if existing_reservation:
        raise HTTPException(status_code=400, detail="Table already registered at the requested time")
    
    
    new_reservation = ResrvationsDetails(
        restaurant_id = resrves.restaurant_id,
        user_id = resrves.user_id,
        table_id = resrves.table_id,
        reservation_time = resrves.reservation_time,
        number_of_guests = resrves.number_of_guests,
        status = "pending",
    )
    db.add(new_reservation)
    db.commit()
    return new_reservation


@reserve_log.get("/all_reservation",response_model=list[ReservationData])
def read_restaurant():
    db_reserv = db.query(ResrvationsDetails).filter(ResrvationsDetails.is_active == True,ResrvationsDetails.is_deleted == False).all()
    if db_reserv is None:
        raise HTTPException(status_code=404, detail="reservation not found")
    return db_reserv



@reserve_log.get("/get_reservation_id",response_model=ReservationData)
def read_single_users(reserve_id: str):
    # user_id = decode_token_user_id(token)
    db_reserv = db.query(ResrvationsDetails).filter(ResrvationsDetails.id == reserve_id,ResrvationsDetails.is_active == True,ResrvationsDetails.is_deleted == False).first()
    
    if db_reserv is None:
        raise HTTPException(status_code=404, detail="reservation not found")
    return db_reserv



@reserve_log.put("/update_reservation_detail")
def update_user_detail(reserv: ReservationData,reserv_id: str):
    # user_id = decode_token_user_id(token)
    
    db_reserv = db.query(ResrvationsDetails).filter(ResrvationsDetails.id == reserv_id).first()
    # breakpoint()
    if db_reserv is None:
        raise HTTPException(status_code=404, detail="reservation detail not found")
    
    db_reserv.restaurant_id    = reserv.restaurant_id,
    db_reserv.user_id   = reserv.user_id,
    db_reserv.table_id    = reserv.table_id,
    db_reserv.reservation_time = reserv.reservation_time,
    db_reserv.number_of_guests = reserv.number_of_guests,
    db_reserv.status = reserv.status,
    
    db.commit()
    return "your detail change succesfully"



@reserve_log.put("/confirm_reservation")
def confirm_reservation(reserve_id: str):
    
    db_reserv = db.query(ResrvationsDetails).filter(ResrvationsDetails.id == reserve_id, ResrvationsDetails.is_active == True, ResrvationsDetails.is_deleted == False).first()
    if db_reserv is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    db_reserv.status = "confirmed"
    db.commit()
    
    user = db.query(CustomerDetail).filter(CustomerDetail.id == db_reserv.user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    table = db.query(TableDetails).filter(TableDetails.id == table_id).first()
    if table is None:
        raise HTTPException(status_code=404, detail="Table not found")
    

    user_email = user.email
    table_id = db_reserv.table_id
    table_number = table.table_number
    
    success, message = send_email(
        sender_email="jenistalaviya404@gmail.com",
        receiver_email=user_email,
        password="zghoimvlnpzerzkv",
        subject="Your Reservation Confirmation",
        body=f"Your reservation has been confirmed. Your table ID is {table_id},Your table number is {table_number}"
    )

    if not success:
        raise HTTPException(status_code=500, detail=message)

    return {"message": "Reservation confirmed, table ID sent to email", "table_id": table_id,"table_number": table_number}



@reserve_log.delete("/delete_reservation")
def delete_user(restaurant_id: str):
    # user_id = decode_token_user_id(token)
    db_reserv = db.query(ResrvationsDetails).filter(ResrvationsDetails.id == restaurant_id,ResrvationsDetails.is_active == True).first()
    if db_reserv is None:
        raise HTTPException(status_code=404, detail="reservation is not found")
    db_reserv.is_active  = False
    db_reserv.is_deleted = True
    
    db.commit()
    return "you deleted successfully"
