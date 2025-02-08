from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db
from schemas import URLBase, ShortURLResponse, LongURLResponse
from crud import create_short_url, get_long_url, get_click_logs, log_click
import qrcode
from io import BytesIO
from fastapi.responses import StreamingResponse

api = APIRouter()

@api.get("/")
def Home_page():
    return {"message": "Welcome to the URL Shortener API!"}

@api.post("/shorten", response_model=ShortURLResponse)
def shorten_url(url: URLBase, db: Session = Depends(get_db)):
    short_url = create_short_url(db, url.long_url, url.custom_short_url, url.expiration_date)
    return {"short_url": f'http://127.0.0.1:8000/{short_url.short_url}','qr_link':f'http://127.0.0.1:8000/qr/{short_url.short_url}'}

@api.get("/{short_url}", response_model=LongURLResponse)
def redirect_url(short_url: str, request:Request, db: Session = Depends(get_db)):
    url_entry = get_long_url(db, short_url)
    if not url_entry:
        raise HTTPException(status_code=404, detail="Short URL not found or expired")
    url_entry.click_count += 1
    log_click(db, short_url, request)
    return {"long_url": url_entry.long_url}

@api.get("/qr/{short_url}")
def generate_qr_code(short_url: str, request:Request, db: Session = Depends(get_db)):
    url_entry = get_long_url(db, short_url)
    if not url_entry:
        raise HTTPException(status_code=404, detail="Short URL not found or expired")
    # Create QR Code
    url_entry.click_count += 1
    log_click(db, short_url, request)
    qr = qrcode.make(url_entry.long_url)
    img_io = BytesIO()
    qr.save(img_io, format="PNG")
    img_io.seek(0)

    return StreamingResponse(img_io, media_type="image/png")

@api.get("/analytics/{short_url}")
def get_analytics(short_url: str, db: Session = Depends(get_db)):
    url_entry =  get_long_url(db, short_url)

    if not url_entry:
        raise HTTPException(status_code=404, detail="Short URL not found")
    
    logs = get_click_logs(db, short_url)
    
    return {
        "short_url": short_url,
        "long_url": url_entry.long_url,
        "total_clicks": url_entry.click_count,
        "click_logs": [
            {"ip": log.ip_address, "user_agent": log.user_agent, "timestamp": log.timestamp}
            for log in logs
        ]
    }
