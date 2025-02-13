from db.company import (
    Company, CompanyCreate, CompanyDelete, CompanyResponse, CompanyUpdate,
    db_create_company,
    db_delete_company,
    db_get_company,
    db_update_company
)
from typing import Annotated
from db.users import oauth2_scheme, validate_token, protect
from fastapi import status

from db.database import get_session, NotFoundError
from sqlmodel import Session
from fastapi import  APIRouter, HTTPException, Depends, APIRouter

router = APIRouter(
    prefix='/company',
)


#Obtener todas las compañias
@router.get("/", tags=["Company"])
def get_company(token: Annotated[str, Depends(oauth2_scheme)],db: Session = Depends(get_session))->list[Company]:
    protect(token)
    try:
        db_comp = db_get_company(db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return db_comp

#Agregar una compañia
@router.post("/", response_model = Company, tags=["Company"])
def create_company(company: CompanyCreate, token: Annotated[str, Depends(oauth2_scheme)],db: Session = Depends(get_session))->Company:
    protect(token)
    try:
        db_comp = db_create_company(company, db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return db_comp

#Actualizar una compañia segun id
@router.put("/{id}", tags=["Company"])
def update_company(id:int, company: CompanyUpdate, token: Annotated[str, Depends(oauth2_scheme)],db: Session = Depends(get_session))->CompanyUpdate:
    protect(token)
    try:
        db_comp = db_update_company(id, company, db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return db_comp

#Eliminar una compañia segun id
@router.delete("/{id}", tags=["Company"])
def delete_company(id: int, token: Annotated[str, Depends(oauth2_scheme)],db: Session = Depends(get_session)):
    protect(token)
    try:
        db_comp = db_delete_company(id, db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return {"message":f"Company {id} eliminado correctamente"}