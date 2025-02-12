from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uvicorn

from app.core.config import get_settings
from app.db.base import get_db
from app.db import models
from app.db.base import engine
from app.schemas.base import (
    Apartment, ApartmentCreate,
    Place, PlaceCreate,
    WhatsAppGroup, WhatsAppGroupCreate,
    Insurance, InsuranceCreate,
    GeneralInfo, GeneralInfoCreate,
    Bank, BankCreate,
    TelecomProvider, TelecomProviderCreate,
    UsefulApp, UsefulAppCreate,
    RAGQuery, RAGResponse
)
from app.services.rag_service import RAGService

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=get_settings().PROJECT_NAME,
    version=get_settings().VERSION,
    openapi_url=f"{get_settings().API_V1_STR}/openapi.json"
)

# Initialize RAG service
rag_service = RAGService()

@app.get("/")
async def root():
    return {"message": "Welcome to Würzburg Student Assistant API"}

@app.post("/apartments/", response_model=Apartment)
def create_apartment(apartment: ApartmentCreate, db: Session = Depends(get_db)):
    db_apartment = models.Apartment(**apartment.model_dump())
    db.add(db_apartment)
    db.commit()
    db.refresh(db_apartment)
    return db_apartment

@app.get("/apartments/", response_model=List[Apartment])
def list_apartments(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    apartments = db.query(models.Apartment).offset(skip).limit(limit).all()
    return apartments

@app.post("/places/", response_model=Place)
def create_place(place: PlaceCreate, db: Session = Depends(get_db)):
    db_place = models.Place(**place.model_dump())
    db.add(db_place)
    db.commit()
    db.refresh(db_place)
    return db_place

@app.get("/places/", response_model=List[Place])
def list_places(
    skip: int = 0,
    limit: int = 10,
    category: str = None,
    cuisine: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Place)
    if category:
        query = query.filter(models.Place.category == category)
    if cuisine:
        query = query.filter(models.Place.cuisine == cuisine)
    return query.offset(skip).limit(limit).all()

# WhatsApp groups endpoints
@app.post("/whatsapp-groups/", response_model=WhatsAppGroup)
def create_whatsapp_group(group: WhatsAppGroupCreate, db: Session = Depends(get_db)):
    db_group = models.WhatsAppGroup(**group.model_dump())
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

@app.get("/whatsapp-groups/", response_model=List[WhatsAppGroup])
def list_whatsapp_groups(
    skip: int = 0,
    limit: int = 10,
    category: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.WhatsAppGroup)
    if category:
        query = query.filter(models.WhatsAppGroup.category == category)
    return query.offset(skip).limit(limit).all()

@app.post("/insurances/", response_model=Insurance)
def create_insurance(insurance: InsuranceCreate, db: Session = Depends(get_db)):
    db_insurance = models.Insurance(**insurance.model_dump())
    db.add(db_insurance)
    db.commit()
    db.refresh(db_insurance)
    return db_insurance

@app.get("/insurances/", response_model=List[Insurance])
def list_insurances(
    skip: int = 0,
    limit: int = 10,
    category: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Insurance)
    if category:
        query = query.filter(models.Insurance.category == category)
    return query.offset(skip).limit(limit).all()

@app.post("/general-info/", response_model=GeneralInfo)
def create_general_info(info: GeneralInfoCreate, db: Session = Depends(get_db)):
    db_info = models.GeneralInfo(**info.model_dump())
    db.add(db_info)
    db.commit()
    db.refresh(db_info)
    return db_info

@app.get("/general-info/", response_model=List[GeneralInfo])
def list_general_info(
    skip: int = 0,
    limit: int = 10,
    category: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.GeneralInfo)
    if category:
        query = query.filter(models.GeneralInfo.category == category)
    return query.offset(skip).limit(limit).all()

@app.post("/banks/", response_model=Bank)
def create_bank(bank: BankCreate, db: Session = Depends(get_db)):
    db_bank = models.Bank(**bank.model_dump())
    db.add(db_bank)
    db.commit()
    db.refresh(db_bank)
    return db_bank

@app.get("/banks/", response_model=List[Bank])
def list_banks(
    skip: int = 0,
    limit: int = 10,
    student_plan: bool = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Bank)
    if student_plan is not None:
        query = query.filter(models.Bank.free_student_plan_available == student_plan)
    return query.offset(skip).limit(limit).all()

@app.post("/telecom-providers/", response_model=TelecomProvider)
def create_telecom_provider(provider: TelecomProviderCreate, db: Session = Depends(get_db)):
    db_provider = models.TelecomProvider(**provider.model_dump())
    db.add(db_provider)
    db.commit()
    db.refresh(db_provider)
    return db_provider

@app.get("/telecom-providers/", response_model=List[TelecomProvider])
def list_telecom_providers(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(models.TelecomProvider).offset(skip).limit(limit).all()

@app.post("/useful-apps/", response_model=UsefulApp)
def create_useful_app(app: UsefulAppCreate, db: Session = Depends(get_db)):
    db_app = models.UsefulApp(**app.model_dump())
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app

@app.get("/useful-apps/", response_model=List[UsefulApp])
def list_useful_apps(
    skip: int = 0,
    limit: int = 10,
    category: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.UsefulApp)
    if category:
        query = query.filter(models.UsefulApp.category == category)
    return query.offset(skip).limit(limit).all()

@app.post("/ask/", response_model=RAGResponse)
async def ask_question(query: RAGQuery):
    try:
        answer, sources = rag_service.query(query.query)
        return RAGResponse(answer=answer, sources=sources)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
