from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
class URL(Base):
    __tablename__ = "urls"
    
    id = Column(Integer, primary_key=True, index=True,autoincrement=True)
    short_url = Column(String, unique=True, nullable=False)
    long_url = Column(String, nullable=False)
    expiration_date = Column(DateTime, nullable=True) 
    click_count = Column(Integer, default=0)

    logs = relationship("ClickLog", back_populates="url")

class ClickLog(Base):
    __tablename__ = "click_logs"

    id = Column(Integer, primary_key=True, index=True,autoincrement=True)
    short_url = Column(String, ForeignKey("urls.short_url"))
    ip_address = Column(String)
    user_agent = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    url = relationship("URL", back_populates="logs")