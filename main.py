from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status
from typing import Annotated
import pandas as pd
from db.database import db_engine, Session, get_session, SQLModel, Executions, Flow_states, Company, NotFoundError
from routers.executions import router as executions_router
from routers.company import router as company_router
from routers.flow_states import router as flow_states_router
from routers.users import router as users_router
from db.file import db_upload_excel
from db.users import oauth2_scheme, validate_token, UserCreate, register_user_db, protect
from dotenv import load_dotenv
from os import getenv

def create_db_and_tables():
    SQLModel.metadata.create_all(db_engine)

tags_metadata=[
    {"name": "File"},
    {"name": "Executions"},
    {"name": "Company"},
    {"name": "Flow States"},
    {"name": "Login"}]
load_dotenv()

app = FastAPI(openapi_tags=tags_metadata)

app.include_router(executions_router)
app.include_router(company_router)
app.include_router(flow_states_router)
app.include_router(users_router)

create_db_and_tables()

@app.on_event("startup")
async def startup_event():
    username = getenv("name")
    email = getenv("correo")
    password= getenv("pass")
    db: Session = next(get_session())
    user_info = UserCreate(
        username=username,
        email=email,
        plain_password=password
    )
    response = register_user_db(user_info, db)
    if not response["success"]:
        print(response["error"])
    else:
        print("Registrado primer usuario")
    

@app.get("/")
def root(token: Annotated[str, Depends(oauth2_scheme)]):
    protect(token)
    return {"Challenge": "SCM"}


#Añadir datos en BDD
@app.post("/upload-excel", tags=["File"])
async def upload_excel(token: Annotated[str, Depends(oauth2_scheme)],db: Session = Depends(get_session), file: UploadFile = File(...)):
    user = validate_token(token, output=True)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authetication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        db_file = await db_upload_excel(db,file)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    
    return db_file




