from db.executions import (
    Executions, ExecutionAverage, ExecutionCompany,
    ExecutionCompanyFlow,ExecutionRanking, ExecutionUpdate,
    ExecutionCreate,ExecutionFlowState,
    db_average_executions,
    db_create_executions,
    db_delete_executions,
    db_executions_company,
    db_executions_company_status,
    db_executions_flow_state,
    db_get_executions,
    db_ranking_executions,
    db_update_executions
)
from typing import Annotated
from db.users import oauth2_scheme, validate_token, protect
from fastapi import status

from db.database import get_session, NotFoundError
from sqlmodel import Session
from fastapi import  APIRouter, HTTPException, Depends, APIRouter

router = APIRouter(
    prefix='/executions',
)

#Agregar una ejecucion
@router.post("/", response_model=Executions, tags=["Executions"])
def create_executions(token: Annotated[str, Depends(oauth2_scheme)],Info: ExecutionCreate, db: Session = Depends(get_session))->ExecutionCreate:
    protect(token)
    db_create = db_create_executions(Info, db)
    return db_create

#Obtener todas las ejecuciones
@router.get("/", tags=["Executions"])
def get_executions(token: Annotated[str, Depends(oauth2_scheme)],db: Session = Depends(get_session))->list[Executions]:
    protect(token)
    try:
        db_exec = db_get_executions(db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return db_exec

#Obtener ranking de ejecuciones finalizadas segun compañia
@router.get("/ranking", tags=["Executions"])
def ranking_executions(token: Annotated[str, Depends(oauth2_scheme)],db: Session = Depends(get_session))-> list[ExecutionRanking]:
    protect(token)
    try:
        db_exec = db_ranking_executions(db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return db_exec

#Obtener duracion promedio de ejecuciones por empresa
@router.get("/average", tags=["Executions"])
def average_executions(token: Annotated[str, Depends(oauth2_scheme)],db: Session = Depends(get_session))->list[ExecutionAverage]:
    protect(token)
    try:
        db_exec = db_average_executions(db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return db_exec

#Obtener ejecuciones segun flow_state
@router.get("/flow_state/{flowid}", tags=["Executions"])
def executions_flow_state(token: Annotated[str, Depends(oauth2_scheme)],flowid: int, db: Session = Depends(get_session))->list[ExecutionFlowState]:
    protect(token)
    try:
        db_exec = db_executions_flow_state(flowid,db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return db_exec

#Obtener todas las ejecuciones de una compañia
@router.get("/company/{companyid}", tags=["Executions"])
def executions_company(token: Annotated[str, Depends(oauth2_scheme)],companyid: int, db: Session = Depends(get_session))-> list[ExecutionCompany]:
    protect(token)
    try:
        db_exec = db_executions_company(companyid,db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return db_exec


#Obtener todas las ejecuciones de una compañia con algun flow_state status
@router.get("/company/{companyid}/flow_state/{flowid}", tags=["Executions"])
def executions_company_status(token: Annotated[str, Depends(oauth2_scheme)],companyid: int, flowid: int, db: Session = Depends(get_session))->list[ExecutionCompanyFlow]:
    protect(token)
    try:
        db_exec = db_executions_company_status(companyid,flowid,db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return db_exec

#Actualizar una ejecucion segun id
@router.put("/{id}", tags=["Executions"])
def update_executions(token: Annotated[str, Depends(oauth2_scheme)],id: int, Info: ExecutionUpdate, db: Session = Depends(get_session))->ExecutionUpdate:
    protect(token)
    try:
        db_exec = db_update_executions(id, Info, db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return db_exec

#Eliminar una ejecucion segun id
@router.delete("/{id}", tags=["Executions"])
def delete_executions(token: Annotated[str, Depends(oauth2_scheme)],id: int, db: Session = Depends(get_session)):
    protect(token)
    try:
        db_exec = db_delete_executions(id, db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return {"message":f"Execution {id} eliminada correctamente"}

