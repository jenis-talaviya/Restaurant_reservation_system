from fastapi import FastAPI,APIRouter

from src.routers.userrouter import customer_log
from src.routers.userrouter import otp_verify
from src.routers.reserve import reserve_log
from src.routers.restro import restaurant_log
from src.routers.reviewrouter import reviews_log
from src.routers.specialrequest import specialrequests_log
from src.routers.tabler import table_log
from src.routers.waitlistrouter import waitlists_log

app = FastAPI()

app. include_router(customer_log)
app.include_router(otp_verify)
app.include_router(reserve_log)
app.include_router(restaurant_log)
app.include_router(reviews_log)
app.include_router(specialrequests_log)
app.include_router(table_log)
app.include_router(waitlists_log)