from fastapi import FastAPI,HTTPException,APIRouter,Depends,Header
from database.database import SessionLocal
from src.models.table import TableDetails
from src.schemas.restaurantschemas import TableData,TablePatchData
import uuid
from datetime import datetime,timedelta
from src.utils.otp import generate_otp,send_otp_via_email
from src.utils.token import get_token,decode_token_password,decode_token_user_email,decode_token_user_id
from logs.log_config import logger



table_log = APIRouter()
db = SessionLocal()

@table_log.post("/table_detail",response_model=TableData)
def create_user(tables:TableData):
    # breakpoint()
    logger.info("enter table detail")
    new_table = TableDetails(
        restaurant_id = tables.restaurant_id,
        table_number = tables.table_number,
        capacity = tables.capacity,
        location_descripation = tables.location_descripation,
    )
    logger.info("add table detail")
    db.add(new_table)
    logger.info("commit table detail")
    db.commit()
    logger.success("detail enter successfully")
    return new_table


@table_log.get("/all_table",response_model=list[TableData])
def read_table():
    logger.info("check codnition and getting data")
    db_table = db.query(TableDetails).filter(TableDetails.is_active == True,TableDetails.is_deleted == False).all()
    if db_table is None:
        logger.error("table not found")
        raise HTTPException(status_code=404, detail="table not found")
    logger.success("table getting successfully")
    return db_table



@table_log.get("/get_table_id",response_model=TableData)
def read_single_users(table_id: str):
    # user_id = decode_token_user_id(token)
    logger.info("enter table id and check condition")
    db_table = db.query(TableDetails).filter(TableDetails.id == table_id,TableDetails.is_active == True,TableDetails.is_deleted == False).first()
    
    if db_table is None:
        logger.error("table not found")
        raise HTTPException(status_code=404, detail="table not found")
    logger.success("getting table detail")
    return db_table



@table_log.put("/update_table_detail")
def update_table_detail(table: TableData,table_id: str):
    # user_id = decode_token_user_id(token)
    logger.info("enter table id and check condition")    
    db_table = db.query(TableDetails).filter(TableDetails.id == table_id).first()
    # breakpoint()
    if db_table is None:
        logger.error("table detail not found")
        raise HTTPException(status_code=404, detail="table detail not found")
    logger.info("enter detail which is change")
    db_table.restaurant_id    = table.restaurant_id,
    db_table.table_number   = table.table_number,
    db_table.capacity     = table.capacity,
    db_table.location_descripation  = table.location_descripation,
    
    logger.info("after change detail commit")
    db.commit()
    logger.success("detail change successfully")
    return "your detail change succesfully"



@table_log.patch("/update_table")
def update_table_detail(table: TablePatchData,table_id: str):
    # user_id = decode_token_user_id(token)
    logger.info("enter table id and check condition")
    db_table = db.query(TableDetails).filter(TableDetails.id == table_id,TableDetails.is_active == True).first()
    if db_table is None:
        logger.error("table not found")
        raise HTTPException(status_code=404, detail="table Not Found")
    update_data = table.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_table, key, value)
    logger.info("commit table after chnaging detail")
    db.commit()
    db.refresh(db_table)
    logger.success("detail changes add successfully")
    return {"message": "Details changed successfully", "User": db_table}



@table_log.delete("/delete_table")
def delete_table(table_id: str):
    # user_id = decode_token_user_id(token)
    logger.info("enter table id and check condition")
    db_table = db.query(TableDetails).filter(TableDetails.id == table_id,TableDetails.is_active == True).first()
    if db_table is None:
        logger.error("table detail not found")
        raise HTTPException(status_code=404, detail="table is not found")
    logger.info("change boolean values")
    db_table.is_active  = False
    db_table.is_deleted = True
    
    logger.info("detail commit")
    db.commit()
    logger.success("delete table successfully")
    return "you deleted successfully"
