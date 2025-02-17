from db.flow_states import (
    Flow_states, Flow_stateCreate, Flow_stateDelete, Flow_stateUpdate,
    db_create_flow_states,
    db_delete_flow_states,
    db_get_flow_states,
    db_update_flow_states
)
from typing import Annotated
from db.users import oauth2_scheme, validate_token, protect
from fastapi import status

from db.database import get_session, NotFoundError
from sqlmodel import Session
from fastapi import  APIRouter, HTTPException, Depends, APIRouter

router = APIRouter(
    prefix='/flow_states',
)

#Obtener todos los estados de flujo
@router.get("/", tags=["Flow States"])
def get_flow_states(token: Annotated[str, Depends(oauth2_scheme)],db: Session = Depends(get_session))->list[Flow_states]:
    
    protect(token)
    try:
        db_flow = db_get_flow_states(db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return db_flow

#Agregar un estado de flujo
@router.post("/", response_model = Flow_states, tags=["Flow States"])
def create_flow_states(flow_state: Flow_stateCreate, token: Annotated[str, Depends(oauth2_scheme)],db: Session = Depends(get_session))->Flow_stateCreate:
    protect(token)
    try:
        db_flow = db_create_flow_states(flow_state,db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return db_flow

#Actualizar un estado de flujo por id
@router.put("/{id}", tags=["Flow States"])
def update_flow_states(id:int, flow_state: Flow_stateUpdate, token: Annotated[str, Depends(oauth2_scheme)],db: Session = Depends(get_session))->Flow_stateUpdate:
    protect(token)
    try:
        db_flow = db_update_flow_states(id, flow_state, db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return db_flow

#Eliminar un estado de flujo por id
@router.delete("/{id}", tags=["Flow States"])
def delete_flow_states(id: int, token: Annotated[str, Depends(oauth2_scheme)],db: Session = Depends(get_session)):
    protect(token)
    try:
        db_flow = db_delete_flow_states(id, db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return {"message":f"Flow_state {id} eliminado correctamente"}
