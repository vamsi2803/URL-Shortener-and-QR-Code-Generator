from fastapi import HTTPException
from sqlalchemy.orm import Session
import models
import shortuuid
from datetime import datetime
from typing import Optional

def create_short_url(db: Session, long_url: str, custom_short_url: Optional[str] = None, expiration_date: Optional[datetime] = None):
    if custom_short_url:
        # Check if the custom short URL already exists
        existing_url = db.query(models.URL).filter(models.URL.short_url == custom_short_url).first()
        if existing_url:
            raise HTTPException(status_code=400, detail="Custom short URL already exists")
        short_url = custom_short_url
    else:
        short_url = shortuuid.ShortUUID().random(length=6)
    db_url = models.URL(short_url=short_url, long_url=long_url, expiration_date=expiration_date)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url

def get_long_url(db: Session, short_url: str):
    url_entry= db.query(models.URL).filter(models.URL.short_url == short_url).first()
    if url_entry and url_entry.expiration_date and url_entry.expiration_date < datetime.utcnow():
        db.delete(url_entry)
        db.commit()
        return None
    return url_entry
def get_click_logs(db: Session, short_url: str):
    return db.query(models.ClickLog).filter(models.ClickLog.short_url == short_url).all()

def log_click(db: Session, short_url: str, request): 
    log_entry = models.ClickLog(
            short_url=short_url,
            ip_address=request.client.host,
            user_agent=request.headers.get("User-Agent")
        )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)

def delete_expired_urls(db: Session):
    expired_urls = db.query(models.URL).filter(models.URL.expiration_date < datetime.utcnow()).all()
    for url in expired_urls:
        db.delete(url)
    db.commit()