from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean
from datetime import datetime, timezone
from .base import Base

class Apartment(Base):
    __tablename__ = "apartments"
    
    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    address = Column(String)
    available_from = Column(String)
    price = Column(Float)
    size = Column(Float)
    rooms = Column(Float)
    image_url = Column(String)
    details_link = Column(String)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

class Place(Base):
    __tablename__ = "places"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    category = Column(String, index=True)
    address = Column(String)
    description = Column(Text)
    price_range = Column(String, nullable=True)  # €, €€, €€€
    rating = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
class Insurance(Base):
    __tablename__ = "insurances"
    
    id = Column(Integer, primary_key=True)
    company_name = Column(String)
    category = Column(String)
    description = Column(Text)
    company_url = Column(String) 
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

class WhatsAppGroup(Base):
    __tablename__ = "whatsapp_groups"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    category = Column(String)
    description = Column(Text)
    invite_link = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
class GeneralInfo(Base):
    __tablename__ = "general_info"
    
    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    category = Column(String, index=True)  
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

class Bank(Base):
    __tablename__ = "banks"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    description = Column(Text)
    website_url = Column(String)
    free_student_plan_available  = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

class TelecomProvider(Base):
    __tablename__ = "telecom_providers"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    description = Column(Text)
    website_url = Column(String)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

class UsefulApp(Base):
    __tablename__ = "useful_apps"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    category = Column(String, index=True) 
    description = Column(Text)
    app_store_url = Column(String, nullable=True)
    play_store_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))