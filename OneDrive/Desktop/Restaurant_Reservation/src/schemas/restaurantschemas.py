from pydantic import BaseModel
from typing import Optional
from datetime import date,time,datetime

class RestaurantData(BaseModel):
    name : str
    cuisine_type : str
    address : str
    email : str
    mobile_no : str
    opening_hours : str
    average_cost : str
    
class RestaurantPatchData(BaseModel):
    name : Optional[str] = None
    cuisine_type : Optional[str] = None
    address : Optional[str] = None
    email : Optional[str] = None
    mobile_no : Optional[str] = None
    opening_hours : Optional[str] = None
    average_cost : Optional[str] = None
    

#--------------------Table----------------------------

class TableData(BaseModel):
    restaurant_id : str
    table_number : str
    capacity : str
    location_descripation : str
    
class TablePatchData(BaseModel):
    restaurant_id : Optional[str] = None
    table_number : Optional[str] = None
    capacity : Optional[str] = None
    location_descripation : Optional[str] = None
    
    
#----------------Reservation---------------------------

class ReservationData(BaseModel):
    restaurant_id : str
    user_id : str
    table_id : str
    reservation_time : datetime
    number_of_guests : str
    status : str
    
class ReservationPatchData(BaseModel):
    restaurant_id : Optional[str] = None
    user_id : Optional[str] = None
    table_id : Optional[str] = None
    reservation_time : Optional[datetime] = None
    number_of_guests : Optional[str] = None
    status : Optional[str] = None
    
#------------------waitlist----------------------------

class WaitlistData(BaseModel):
    restaurant_id : str
    user_id : str
    waitlist_time : datetime
    number_of_guest : str
    status : str
    
class WaitlistPatchData(BaseModel):
    restaurant_id : Optional[str] = None
    user_id : Optional[str] = None
    waitlist_time : Optional[datetime] = None
    number_of_guest : Optional[str] = None
    status : Optional[str] = None
    
#----------------review------------------------------

class ReviewData(BaseModel):
    restaurant_id : str
    user_id : str
    rating : str
    comment : str
    
class ReviewPatchData(BaseModel):
    restaurant_id : Optional[str] = None
    user_id : Optional[str] = None
    rating : Optional[str] = None
    comment : Optional[str] = None
    

#---------------special_request--------------------

class SpecialrequestData(BaseModel):
    reservation_id : str
    status : str
    request : str
    
class SpecialrequestPatchData(BaseModel):
    reservation_id : Optional[str] = None
    status : Optional[str] = None
    request : Optional[str] = None