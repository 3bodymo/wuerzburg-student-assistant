from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ApartmentBase(BaseModel):
    title: str
    address: str
    price: float
    size: float
    rooms: float
    available_from: str
    image_url: str
    details_link: str

class ApartmentCreate(ApartmentBase):
    pass

class Apartment(ApartmentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PlaceBase(BaseModel):
    name: str
    category: str
    address: str
    description: str
    price_range: Optional[str]
    rating: Optional[float]

class PlaceCreate(PlaceBase):
    pass

class Place(PlaceBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class WhatsAppGroupBase(BaseModel):
    name: str
    category: str
    description: str
    invite_link: str

class WhatsAppGroupCreate(WhatsAppGroupBase):
    pass

class WhatsAppGroup(WhatsAppGroupBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class InsuranceBase(BaseModel):
    company_name: str
    category: str
    description: str
    company_url: str

class InsuranceCreate(InsuranceBase):
    pass

class Insurance(InsuranceBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class GeneralInfoBase(BaseModel):
    title: str
    category: str
    description: str

class GeneralInfoCreate(GeneralInfoBase):
    pass

class GeneralInfo(GeneralInfoBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class BankBase(BaseModel):
    name: str
    description: str
    website_url: str
    free_student_plan_available: bool

class BankCreate(BankBase):
    pass

class Bank(BankBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TelecomProviderBase(BaseModel):
    name: str
    description: str
    website_url: str

class TelecomProviderCreate(TelecomProviderBase):
    pass

class TelecomProvider(TelecomProviderBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UsefulAppBase(BaseModel):
    name: str
    category: str
    description: str
    app_store_url: Optional[str] = None
    play_store_url: Optional[str] = None

class UsefulAppCreate(UsefulAppBase):
    pass

class UsefulApp(UsefulAppBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RAGQuery(BaseModel):
    query: str

class RAGResponse(BaseModel):
    answer: str