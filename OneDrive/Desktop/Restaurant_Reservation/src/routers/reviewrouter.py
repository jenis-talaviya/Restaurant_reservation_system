from fastapi import FastAPI,HTTPException,APIRouter,Depends,Header
from database.database import SessionLocal
from src.models.reviews import ReviewDetails
from src.schemas.restaurantschemas import ReviewData,ReviewPatchData
import uuid
from datetime import datetime,timedelta
from src.utils.otp import generate_otp,send_otp_via_email
from src.utils.token import get_token,decode_token_password,decode_token_user_email,decode_token_user_id
from logs.log_config import logger



reviews_log = APIRouter()
db = SessionLocal()

@reviews_log.post("/review_detail",response_model=ReviewData)
def create_review(review:ReviewData):
    # breakpoint()
    logger.info("enter review detail")
        
    new_review = ReviewDetails(
        restaurant_id = review.restaurant_id,
        user_id = review.user_id,
        rating = review.rating,
        comment = review.comment,
    )
    logger.info("add detail in database")
    db.add(new_review)
    logger.info("commit detail after")
    db.commit()
    logger.success("detail added successfully")
    return new_review


@reviews_log.get("/all_review",response_model=list[ReviewData])
def read_reviews():
    logger.info("check the condition")
    db_review = db.query(ReviewDetails).filter(ReviewDetails.is_active == True,ReviewDetails.is_deleted == False).all()
    if db_review is None:
        logger.error("review is not found")
        raise HTTPException(status_code=404, detail="reviews not found")
    logger.success("review getting successfully")
    return db_review



@reviews_log.get("/get_review_id",response_model=ReviewData)
def read_single_review(review_id: str):
    # user_id = decode_token_user_id(token)
    logger.info("enter review_id and check the condition")
    db_review = db.query(ReviewDetails).filter(ReviewDetails.id == review_id,ReviewDetails.is_active == True,ReviewDetails.is_deleted == False).first()
    
    if db_review is None:
        logger.error("review is not found")
        raise HTTPException(status_code=404, detail="review not found")
    logger.success("review getting successfully")
    return db_review



@reviews_log.put("/update_review_detail")
def update_review_detail(review: ReviewData,review_id: str):
    # user_id = decode_token_user_id(token)
    logger.info("enter review_id and check the condition")    
    db_review = db.query(ReviewDetails).filter(ReviewDetails.id == review_id).first()
    # breakpoint()
    if db_review is None:
        logger.error("review is not found")
        raise HTTPException(status_code=404, detail="review detail not found")
    
    logger.info("chnage detail or update")
    db_review.restaurant_id    = review.restaurant_id,
    db_review.user_id   = review.user_id,
    db_review.rating    = review.rating,
    db_review.comment = review.comment,
    
    logger.info("commit detail after updating")
    db.commit()
    logger.success("review change successfully")
    return "your detail change succesfully"



@reviews_log.patch("/update_review")
def update_review(review: ReviewPatchData,review_id: str):
    # user_id = decode_token_user_id(token)
    logger.info("enter review_id and check the condition")    
    db_review = db.query(ReviewDetails).filter(ReviewDetails.id == review_id,ReviewDetails.is_active == True).first()
    if db_review is None:
        logger.error("review is not found")
        raise HTTPException(status_code=404, detail="review Not Found")
    update_data = review.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_review, key, value)
    logger.info("commit detail after updating")
    db.commit()
    db.refresh(db_review)
    logger.success("review updating successfully")
    return {"message": "Details changed successfully", "User": db_review}



@reviews_log.delete("/delete_review")
def delete_review(review_id: str):
    logger.info("enter review_id and check the condition")
    # user_id = decode_token_user_id(token)
    db_review = db.query(ReviewDetails).filter(ReviewDetails.id == review_id,ReviewDetails.is_active == True).first()
    if db_review is None:
        logger.error("review is not found")
        raise HTTPException(status_code=404, detail="review is not found")
    logger.info("boolean values")
    db_review.is_active  = False
    db_review.is_deleted = True
    
    logger.info("commit detail after updating")
    db.commit()
    logger.success("review deleting successfully")
    return "you deleted successfully"
