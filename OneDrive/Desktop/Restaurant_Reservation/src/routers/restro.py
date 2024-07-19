from fastapi import FastAPI,HTTPException,APIRouter,Depends,Header
from database.database import SessionLocal
from src.models.Restaurants import RestaurantDetail
from src.schemas.restaurantschemas import RestaurantData,RestaurantPatchData
import uuid
from typing import Optional
from datetime import datetime,timedelta
from src.utils.otp import generate_otp,send_otp_via_email
from src.utils.token import get_token,decode_token_password,decode_token_user_email,decode_token_user_id
from logs.log_config import logger



restaurant_log = APIRouter()
db = SessionLocal()

@restaurant_log.post("/restaurant_detail",response_model=RestaurantData)
def create_user(restaurants:RestaurantData):
    # breakpoint()
    
    logger.info("enter restaurant detail")
    new_restaurant = RestaurantDetail(
        name = restaurants.name,
        cuisine_type = restaurants.cuisine_type,
        address = restaurants.address,
        email = restaurants.email,
        mobile_no = restaurants.mobile_no,
        opening_hours = restaurants.opening_hours,
        average_cost = restaurants.average_cost,
    )
    logger.info("add restaurant detail")
    db.add(new_restaurant)
    logger.info("commit restaurant detail")
    db.commit()
    logger.success("restaurnt detail added successfully")
    return new_restaurant


@restaurant_log.get("/all_restaurant",response_model=list[RestaurantData])
def read_restaurant():
    logger.info("check condition")
    db_restro = db.query(RestaurantDetail).filter(RestaurantDetail.is_active == True,RestaurantDetail.is_deleted == False).all()
    if db_restro is None:
        logger.error("restaurant detail not found")
        raise HTTPException(status_code=404, detail="restaurant not found")
    logger.success("detail get successfully")
    return db_restro



@restaurant_log.get("/all_restaurants", response_model=list[RestaurantData])
def read_restaurant(cuisine_type: Optional[str] = None):
    logger.info("enter cuisine type and check condition")
    query = db.query(RestaurantDetail).filter(RestaurantDetail.is_active == True, RestaurantDetail.is_deleted == False)
    logger.info("check condition")
    if cuisine_type:
        logger.info("check cuisine type with restaurant table")
        query = query.filter(RestaurantDetail.cuisine_type == cuisine_type)
    
    db_restro = query.all()
    
    logger.info("check cuisine type not available")
    if not db_restro:
        logger.error("restaurant not found according to cuisine type")
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    logger.success("detail found successfully")
    return db_restro



@restaurant_log.get("/get_restaurant_id",response_model=RestaurantData)
def read_single_users(restauran_id: str):
    logger.info("enter the restaurant id")
    # user_id = decode_token_user_id(token)
    db_restro = db.query(RestaurantDetail).filter(RestaurantDetail.id == restauran_id,RestaurantDetail.is_active == True,RestaurantDetail.is_deleted == False).first()
    logger.info("if id not found in table")
    if db_restro is None:
        logger.error("restaurant not available or not entered")
        raise HTTPException(status_code=404, detail="restro not found")
    logger.success("detail get successfully")
    return db_restro



@restaurant_log.put("/update_restaurant_detail")
def update_user_detail(restro: RestaurantData,restaurant_id: str):
    # user_id = decode_token_user_id(token)
    logger.info("enter restaurant id")
    db_restro = db.query(RestaurantDetail).filter(RestaurantDetail.id == restaurant_id).first()
    # breakpoint()
    logger.info("check conditions")
    if db_restro is None:
        logger.error("restaurant is detail is not found")
        raise HTTPException(status_code=404, detail="restro detail not found")
    logger.info("enter detail")
    db_restro.name    = restro.name,
    db_restro.cuisine_type    = restro.cuisine_type,
    db_restro.address   = restro.address,
    db_restro.email    = restro.email,
    db_restro.mobile_no= restro.mobile_no,
    db_restro.opening_hours = restro.opening_hours,
    db_restro.average_cost= restro.average_cost,
    
    logger.info("commit the detail")
    db.commit()
    logger.success("detail change successfully")
    return "your detail change succesfully"



@restaurant_log.patch("/update_restaurant")
def update_data(restro: RestaurantPatchData,restaurant_id: str):
    # user_id = decode_token_user_id(token)
    logger.info("enter and check restaurant id")
    db_restro = db.query(RestaurantDetail).filter(RestaurantDetail.id == restaurant_id,RestaurantDetail.is_active == True).first()
    logger.info("check codition")
    if db_restro is None:
        logger.error("restaurant detail not found")
        raise HTTPException(status_code=404, detail="restro Not Found")
    logger.info("update detail")
    update_data = restro.dict(exclude_unset=True)
    for key, value in update_data.items():
        logger.info("add detail update")
        setattr(db_restro, key, value)
    logger.info("commit changes")
    db.commit()
    db.refresh(db_restro)
    logger.success("detail save successfully after changing")
    return {"message": "Details changed successfully", "User": db_restro}



@restaurant_log.delete("/delete_restaurant")
def delete_user(restaurant_id: str):
    logger.info("find restaurant using id")
    # user_id = decode_token_user_id(token)
    db_restro = db.query(RestaurantDetail).filter(RestaurantDetail.id == restaurant_id,RestaurantDetail.is_active == True).first()
    if db_restro is None:
        logger.error("restaurant detail not found")
        raise HTTPException(status_code=404, detail="restro is not found")
    logger.info("change boolean value")
    db_restro.is_active  = False
    db_restro.is_deleted = True
    
    logger.info("commit restaurant")
    db.commit()
    logger.success("deleted successfully")
    return "you deleted successfully"
