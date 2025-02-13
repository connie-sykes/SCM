from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Annotated
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from jwt import encode, decode, exceptions
from fastapi.security import OAuth2PasswordBearer
from os import getenv
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from db.database import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
ALGORITHM = getenv("ALGORITHM")
SECRET = getenv("SECRET_KEY")

class UserData(BaseModel):
    username: str
    email: EmailStr
    hashed_password: str

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    plain_password: str

class Token(BaseModel):
    access_token:str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

#Compara la pass () con la hasheada
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

#Hashea la contrase;a
def get_password_hash(password):
    return pwd_context.hash(password)

#Checkea DB si calza la contrase;a con la del formulario
def authenticate_user(username:str,password:str, db:Session):
    user = get_user(username, db) #Traer el usuario desde la BD
    if not user: #Si no existe, retorna falso
        return False
    if not verify_password(password, user[0].hashed_password): #Si pass no calza, retorna falso
        return False
    return user

#Fecha expiracion token
def expire_date(days: int):
    date = datetime.now()
    new_date = date + timedelta(days)
    return new_date

#Crea el token de acceso
def create_token(data: dict):
    token = encode(payload={**data, "exp": expire_date(2)}, key=SECRET, algorithm=ALGORITHM)
    return token

#Valida el token
def validate_token(token, output=False):
    try:
        if output:
            return decode(token, key=SECRET, algorithms=[ALGORITHM])
        decode(token, key=SECRET, algorithms=[ALGORITHM])
    except exceptions.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid Token")
    except exceptions.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Expired token")

#Flujo validacion token
def protect(token: Annotated[str, Depends(oauth2_scheme)]):
    user = validate_token(token, output=True)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authetication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

#Obtiene los datos del usuario desde BD
def get_user(username: str, db: Session)->UserData:
    statement = (
        select(User) 
        .where(User.username == username) 
    )
    results = db.exec(statement).all()

    return results

#Crea un usuario en la BD
#   Se debe retornar un dict y no un UserData por su uso en startup, si falla se cae todo
def register_user_db(Info: UserCreate, db: Session)->dict:
    new_password = get_password_hash(Info.plain_password)
    db_execution = User(**Info.dict()) #Creo un dict con Info del user ingresada
    db_execution.hashed_password = new_password #Hasheada
    db.add(db_execution)
    try:
        db.commit()
        db.refresh(db_execution)
        return {"success": True, "user": db_execution} 
    except IntegrityError:
        db.rollback()  # Deshacer el commit si hay un error
        return {
            "success": False,
            "error": "El nombre de usuario ya existe."
        }


#Elimina un usuario de la BD
def delete_user_db(username: str, db: Session)->UserData:
    statement = db.query(User).filter(User.username == username).first()
    if not statement:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(statement)
    db.commit()
    return {"message":f"Usuario '{username}' eliminado correctamente"}

