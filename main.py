from fastapi import FastAPI
from database import engine, Base, get_db
from fastapi.middleware.cors import CORSMiddleware
from routes import api
from apscheduler.schedulers.background import BackgroundScheduler
from crud import delete_expired_urls
app = FastAPI()

app.include_router(api)

app.add_middleware(CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine) 

# Schedule deletion of expired URLs
scheduler = BackgroundScheduler()
scheduler.add_job(delete_expired_urls, "interval", minutes=30, args=[next(get_db())])  # Deletes expired URLs every 30 minutes
scheduler.start()
