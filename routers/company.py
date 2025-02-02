from db.company import (
    Company, CompanyCreate, CompanyDelete, CompanyResponse, CompanyUpdate,
    db_create_company,
    db_delete_company,
    db_get_company,
    db_update_company
)
from db.database import get_session, NotFoundError
from sqlmodel import Session
from fastapi import  APIRouter, HTTPException, Depends, APIRouter

router = APIRouter(
    prefix='/company',
)


#Obtener todas las compañias
@router.get("/", tags=["Company"])
def get_company(db: Session = Depends(get_session))->list[Company]:
    try:
        db_comp = db_get_company(db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return db_comp

#Agregar una compañia
@router.post("/", response_model = Company, tags=["Company"])
def create_company(company: CompanyCreate, db: Session = Depends(get_session))->Company:
    try:
        db_comp = db_create_company(company, db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return db_comp

#Actualizar una compañia segun id
@router.put("/{id}", tags=["Company"])
def update_company(id:int, company: CompanyUpdate, db: Session = Depends(get_session))->CompanyUpdate:
    try:
        db_comp = db_update_company(id, company, db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return db_comp

#Eliminar una compañia segun id
@router.delete("/{id}", tags=["Company"])
def delete_company(id: int, db: Session = Depends(get_session)):
    try:
        db_comp = db_delete_company(id, db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return {"message":f"Company {id} eliminado correctamente"}