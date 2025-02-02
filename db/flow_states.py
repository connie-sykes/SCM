from pydantic import BaseModel
from sqlmodel import SQLModel, Field, select, func, text
from db.database import get_session
from sqlmodel import Session
from fastapi import  HTTPException, Depends
from .database import Flow_states, Session, get_session, SQLModel


class Flow_stateCreate(BaseModel):
    status: str

class Flow_stateUpdate(BaseModel):
    status: str

class Flow_stateDelete(BaseModel):
    id: int

#Obtener todos los estados de flujo
def db_get_flow_states(db: Session = Depends(get_session)):
    statement = db.exec(select(Flow_states)).all()
    return statement

#Agregar un estado de flujo
def db_create_flow_states(flow_state: Flow_stateCreate, db: Session = Depends(get_session)):
    statement = Flow_states(**flow_state.dict())
    db.add(statement)
    db.commit()
    db.refresh(statement)
    return statement

#Actualizar un estado de flujo por id
def db_update_flow_states(id:int, flow_state: Flow_stateUpdate, db: Session = Depends(get_session)):
    statement = db.get(Flow_states,id)
    if not statement:
        raise HTTPException(status_code=404, detail="statement not found")
    data = flow_state.dict(exclude_unset=True)
    for key, value in data.items():
        setattr(statement, key, value)
    db.add(statement)
    db.commit()
    db.refresh(statement)
    return statement

#Eliminar un estado de flujo por id
def db_delete_flow_states(id: int, db: Session = Depends(get_session)):
    statement = db.get(Flow_states, id)
    if not statement:
        raise HTTPException(status_code=404, detail="Flow State not found")
    db.delete(statement)
    db.commit()
    return {"message":f"Flow_state {id} eliminado correctamente"}
