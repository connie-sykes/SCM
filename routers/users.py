from typing import Annotated
from db.database import get_session, User, NotFoundError
from sqlmodel import Session
from fastapi import  APIRouter, HTTPException, Depends, APIRouter, status
from fastapi.security import OAuth2PasswordRequestForm
from db.users import (
    protect, create_token, authenticate_user,
    UserData, 
    UserCreate, register_user_db, oauth2_scheme, delete_user_db
    )

router = APIRouter()

#Obtiene el usuario logeado actual
@router.get("/me", tags=["Login"])
async def who_am_i(current_user: Annotated[User, Depends(protect)]):
    return current_user

#Login with access token 
#   Token must be in /token endpoint, not /users/token
@router.post("/token")
async def login_for_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_session)):
    user =  authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or pass", headers={"WWW-Authenticate":"Bearer"},)
    access_token =  create_token(data={"sub": str(user[0].username)})

    return {'access_token' : access_token}

#Crear usuario!
@router.post("/users",tags=["Login"])
def register_user(token: Annotated[str, Depends(oauth2_scheme)],Info: UserCreate, db: Session=Depends(get_session))->dict:
    protect(token)
    db_register = register_user_db(Info, db)
    if not db_register["success"]:
        return {
            "success": False,
            "error": db_register["error"]  # Retorna el mensaje de error
        }
    
    return {
        "success": True,
        "user": db_register["user"]  # Retorna el usuario creado
    }

#Borrar usuario!
@router.delete("/users",tags=["Login"])
def delete_user(username: str, token: Annotated[str, Depends(oauth2_scheme)],db: Session = Depends(get_session)):
    protect(token)
    try:
        db_flow = delete_user_db(username, db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return {"message":f"Usuario '{username}' eliminado correctamente"}