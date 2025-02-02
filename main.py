from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, APIRouter
import pandas as pd
from db.database import db_engine, Session, get_session, SQLModel, Executions, Flow_states, Company, NotFoundError
from routers.executions import router as executions_router
from routers.company import router as company_router
from routers.flow_states import router as flow_states_router
from db.file import db_upload_excel

def create_db_and_tables():
    SQLModel.metadata.create_all(db_engine)

tags_metadata=[
    {"name": "File"},
    {"name": "Executions"},
    {"name": "Company"},
    {"name": "Flow States"}]
app = FastAPI(openapi_tags=tags_metadata)

app.include_router(executions_router)
app.include_router(company_router)
app.include_router(flow_states_router)

create_db_and_tables()

@app.get("/")
def root():
    return {"Challenge":"Practicante SCM"}


#Añadir datos en BDD
@app.post("/upload-excel", tags=["File"])
async def upload_excel(file: UploadFile = File(...), db: Session = Depends(get_session)):
    try:
        db_file = await db_upload_excel(file, db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    
    return db_file




