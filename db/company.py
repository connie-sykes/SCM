from pydantic import BaseModel
from sqlmodel import SQLModel, select
from sqlmodel import Session
from fastapi import  HTTPException, Depends
from .database import Company, Session, get_session

class CompanyCreate(BaseModel):
    nombre: str

class CompanyResponse(BaseModel):
    id: int
    nombre: str

class CompanyUpdate(BaseModel):
    nombre: str

class CompanyDelete(BaseModel):
    id: int

#Obtener todas las compañias
def db_get_company(db: Session):
    statement = db.exec(select(Company)).all()
    return statement

#Agregar una compañia
def db_create_company(company: CompanyCreate, db: Session):
    statement = Company(**company.dict())
    db.add(statement)
    db.commit()
    db.refresh(statement)
    return statement

#Actualizar una compañia segun id
def db_update_company(id:int, company: CompanyUpdate, db: Session):
    statement = db.get(Company,id)
    if not statement:
        raise HTTPException(status_code=404, detail="statement not found")
    data = company.dict(exclude_unset=True)
    for key, value in data.items():
        setattr(statement, key, value)
    db.add(statement)
    db.commit()
    db.refresh(statement)
    return statement

#Eliminar una compañia segun id
def db_delete_company(id: int, db: Session):
    statement = db.get(Company, id)
    if not statement:
        raise HTTPException(status_code=404, detail="Flow State not found")
    db.delete(statement)
    db.commit()
    return {"message":f"Company {id} eliminado correctamente"}