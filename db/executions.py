from datetime import date, datetime
from pydantic import BaseModel
from sqlmodel import select, func, text, Field
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
import pandas as pd
from .database import Company, Executions, Flow_states, Session, get_session, SQLModel


class ExecutionCreate(BaseModel):
    fecha_creacion: datetime
    fecha_termino: datetime | None = None 
    start_dtm: date
    end_dtm: date
    company_id: int 
    estado: str 
    status_id: int

class ExecutionRanking(BaseModel): #La query debe decir estado=finalizado, company_id={id}, top 10?
    ejecuciones_finalizadas:int
    nombre_empresa:str

class ExecutionAverage(BaseModel): #Query debe retornar average start_dtm y end_dtm
    company_name: str
    duration_in_seconds: float

class ExecutionUpdate(BaseModel):
    fecha_creacion: datetime | None = None 
    fecha_termino: datetime | None = None
    start_dtm: date | None = None
    end_dtm: date | None = None
    company_id: int | None = None
    estado: str | None = None
    status_id: int | None = None

#Company Executions
class ExecutionCompany(BaseModel):
    company_name: str
    fecha_creacion: datetime | None = None 
    fecha_termino: datetime | None = None
    start_dtm: date | None = None
    end_dtm: date | None = None
    estado: str 
    status_id: int 
    flow_status: str

#Executions Flow_state
class ExecutionFlowState(BaseModel):
    flow_state: str
    exec_id: int 
    company_name: str
    fecha_creacion: datetime | None = None 
    fecha_termino: datetime | None = None
    start_dtm: date | None = None
    end_dtm: date | None = None

#Executions Company-flow
class ExecutionCompanyFlow(BaseModel):
    flow_state: str
    company_name: str
    exec_id: int 
    fecha_creacion: datetime | None = None 
    fecha_termino: datetime | None = None
    start_dtm: date | None = None
    end_dtm: date | None = None
    estado: str

#Agregar una ejecucion
def db_create_executions(Info: ExecutionCreate, db: Session):
    db_execution = Executions(**Info.dict())
    db.add(db_execution)
    db.commit()
    db.refresh(db_execution)
    return db_execution

#Obtener todas las ejecuciones
def db_get_executions(db: Session):
    statement = db.exec(select(Executions)).all()
    return statement

#Obtener ranking de ejecuciones finalizadas segun compañia
def db_ranking_executions(db: Session):
    statement = (
        select(Company.nombre.label("Nombre_empresa"),func.count(Executions.estado).label("Ejecuciones_finalizadas"))
        .join(Company, Company.id == Executions.company_id)
        .where(Executions.estado == 'finalizado')
        .group_by(Company.id, Company.nombre)
        .order_by(func.count(Executions.estado).desc())
    )
    results = db.exec(statement).all()

    rankings = [
        ExecutionRanking(ejecuciones_finalizadas=row[1], nombre_empresa=row[0]) for row in results
        ]
    return rankings

#Obtener duracion promedio de ejecuciones por empresa
def db_average_executions(db: Session):
    statement = (
        select(Company.nombre.label("Nombre_empresa"), func.avg(func.abs(func.datediff(text('Second'), Executions.fecha_termino, Executions.fecha_creacion))).label("Duracion"))
        .join(Company, Company.id == Executions.company_id)
        .where(Executions.fecha_termino.isnot(None))
        .group_by(Company.id, Company.nombre)
        .order_by("Duracion")
    )
    results = db.exec(statement).all()

    durations = [
        ExecutionAverage(company_name=row.Nombre_empresa,duration_in_seconds=row.Duracion) for row in results
    ]
    return durations

#Obtener ejecuciones segun flow_state
def db_executions_flow_state(flowid: int, db: Session):
    statement = (
        select(Company.nombre.label("Nombre_empresa"),Executions, Flow_states)
        .join(Company, Company.id == Executions.company_id)
        .join(Flow_states, Executions.status_id == Flow_states.id)
        .where(Executions.status_id == flowid)
    )
    results = db.exec(statement).all()

    exec_flow_state = [
        ExecutionFlowState(
            flow_state= row.Flow_states.status, 
            exec_id = row.Executions.id,
            company_name= row.Nombre_empresa,
            fecha_creacion= row.Executions.fecha_creacion,
            fecha_termino= row.Executions.fecha_termino,
            start_dtm= row.Executions.start_dtm,
            end_dtm= row.Executions.end_dtm) for row in results
        ]
    return exec_flow_state

#Obtener todas las ejecuciones de una compañia
def db_executions_company(companyid: int, db: Session):
    statement = (
        select(Company.nombre.label("Nombre_empresa"),Executions, Flow_states)
        .join(Company, Company.id == Executions.company_id)
        .join(Flow_states, Executions.status_id == Flow_states.id)
        .where(Company.id == companyid)
    )
    results = db.exec(statement).all()

    exec_company = [
        ExecutionCompany(
            company_name=row.Nombre_empresa ,
            fecha_creacion=row.Executions.fecha_creacion,
            fecha_termino=row.Executions.fecha_termino,
            start_dtm= row.Executions.start_dtm,
            end_dtm= row.Executions.end_dtm,
            estado= row.Executions.estado,
            status_id= row.Executions.status_id,
            flow_status= row.Flow_states.status) for row in results
        ]
    return exec_company


#Obtener todas las ejecuciones de una compañia con algun flow_state status
def db_executions_company_status(companyid: int, flowid: int, db: Session):
    statement = (
        select(Company.nombre.label("Nombre_empresa"),Executions, Flow_states)
        .join(Company, Company.id == Executions.company_id)
        .join(Flow_states, Executions.status_id == Flow_states.id)
        .where((Company.id == companyid) & (Flow_states.id==flowid))
    )
    results = db.exec(statement).all()

    exec_company_flow = [
        ExecutionCompanyFlow(
            flow_state= row.Flow_states.status,
            company_name= row.Nombre_empresa ,
            exec_id = row.Executions.id,
            fecha_creacion= row.Executions.fecha_creacion,
            fecha_termino= row.Executions.fecha_termino,
            start_dtm= row.Executions.start_dtm,
            end_dtm= row.Executions.end_dtm,
            estado= row.Executions.estado) for row in results
        ]
    return exec_company_flow



#Eliminar una ejecucion segun id
def db_delete_executions(id: int, db: Session):
    execution = db.get(Executions, id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    db.delete(execution)
    db.commit()
    return {"message":f"Execution {id} eliminada correctamente"}

#Actualizar una ejecucion segun id
def db_update_executions(id: int, Info: ExecutionUpdate, db: Session):
    execution = db.get(Executions,id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    data = Info.dict(exclude_unset=True)
    for key, value in data.items():
        setattr(execution, key, value)
    db.add(execution)
    db.commit()
    db.refresh(execution)
    return execution