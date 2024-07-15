from fastapi import FastAPI,HTTPException,APIRouter,Depends,Header
from database.database import SessionLocal
from src.models.Restaurants import RestaurantDetail
from src.schemas.restaurantschemas import RestaurantData,RestaurantPatchData
import uuid
from typing import Optional
from datetime import datetime,timedelta
from src.utils.otp import generate_otp,send_otp_via_email
from src.utils.token import get_token,decode_token_password,decode_token_user_email,decode_token_user_id



restaurant_log = APIRouter()
db = SessionLocal()

@restaurant_log.post("/restaurant_detail",response_model=RestaurantData)
def create_user(restaurants:RestaurantData):
    # breakpoint()
        
    new_restaurant = RestaurantDetail(
        name = restaurants.name,
        cuisine_type = restaurants.cuisine_type,
        address = restaurants.address,
        email = restaurants.email,
        mobile_no = restaurants.mobile_no,
        opening_hours = restaurants.opening_hours,
        average_cost = restaurants.average_cost,
    )
    db.add(new_restaurant)
    db.commit()
    return new_restaurant


@restaurant_log.get("/all_restaurant",response_model=list[RestaurantData])
def read_restaurant():
    db_restro = db.query(RestaurantDetail).filter(RestaurantDetail.is_active == True,RestaurantDetail.is_deleted == False).all()
    if db_restro is None:
        raise HTTPException(status_code=404, detail="restaurant not found")
    return db_restro



@restaurant_log.get("/all_restaurants", response_model=list[RestaurantData])
def read_restaurant(cuisine_type: Optional[str] = None):
    query = db.query(RestaurantDetail).filter(RestaurantDetail.is_active == True, RestaurantDetail.is_deleted == False)
    
    if cuisine_type:
        query = query.filter(RestaurantDetail.cuisine_type == cuisine_type)
    
    db_restro = query.all()
    
    if not db_restro:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    return db_restro



@restaurant_log.get("/get_restaurant_id",response_model=RestaurantData)
def read_single_users(restauran_id: str):
    # user_id = decode_token_user_id(token)
    db_restro = db.query(RestaurantDetail).filter(RestaurantDetail.id == restauran_id,RestaurantDetail.is_active == True,RestaurantDetail.is_deleted == False).first()
    
    if db_restro is None:
        raise HTTPException(status_code=404, detail="restro not found")
    return db_restro



@restaurant_log.put("/update_restaurant_detail")
def update_user_detail(restro: RestaurantData,restaurant_id: str):
    # user_id = decode_token_user_id(token)
    
    db_restro = db.query(RestaurantDetail).filter(RestaurantDetail.id == restaurant_id).first()
    # breakpoint()
    if db_restro is None:
        raise HTTPException(status_code=404, detail="restro detail not found")
    
    db_restro.name    = restro.name,
    db_restro.cuisine_type    = restro.cuisine_type,
    db_restro.address   = restro.address,
    db_restro.email    = restro.email,
    db_restro.mobile_no= restro.mobile_no,
    db_restro.opening_hours = restro.opening_hours,
    db_restro.average_cost= restro.average_cost,
    
    db.commit()
    return "your detail change succesfully"



@restaurant_log.patch("/update_restaurant")
def update_data(restro: RestaurantPatchData,restaurant_id: str):
    # user_id = decode_token_user_id(token)
    db_restro = db.query(RestaurantDetail).filter(RestaurantDetail.id == restaurant_id,RestaurantDetail.is_active == True).first()
    if db_restro is None:
        raise HTTPException(status_code=404, detail="restro Not Found")
    update_data = restro.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_restro, key, value)
    db.commit()
    db.refresh(db_restro)
    return {"message": "Details changed successfully", "User": db_restro}



@restaurant_log.delete("/delete_restaurant")
def delete_user(restaurant_id: str):
    # user_id = decode_token_user_id(token)
    db_restro = db.query(RestaurantDetail).filter(RestaurantDetail.id == restaurant_id,RestaurantDetail.is_active == True).first()
    if db_restro is None:
        raise HTTPException(status_code=404, detail="restro is not found")
    db_restro.is_active  = False
    db_restro.is_deleted = True
    
    db.commit()
    return "you deleted successfully"
