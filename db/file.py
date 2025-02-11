from sqlmodel import Session
from io import BytesIO
import numpy as np
from sqlalchemy import Table, MetaData
from .database import Session
from fastapi import File, UploadFile, HTTPException
import pandas as pd

def bulk_insert(df: pd.DataFrame, tableName: str, db: Session):
    df = df.replace({np.nan: None})
    listToWrite = df.to_dict(orient='records')
    metadata = MetaData()
    table = Table(tableName, metadata, autoload_with=db.get_bind())
    db.exec(table.insert().values(listToWrite))
    db.commit()


async def db_upload_excel(db: Session, file: UploadFile = File(...)):
    #Validacion del archivo
    if not file.filename.endswith('.xlsx'):
        return HTTPException(status_code=400, detail="El archivo debe ser Excel")
    
    contents = await file.read()
    xls = pd.ExcelFile(BytesIO(contents))
    df1 = pd.read_excel(xls, 'executions')
    df2 = pd.read_excel(xls, 'flows_states')
    df3 = pd.read_excel(xls, 'company')

    if not all(col in df1.columns for col in ['id','fecha_creacion','fecha_termino','start_dtm','end_dtm','company_id','estado','status_id']):
        raise HTTPException(status_code=400, detail="Columnas faltantes en el archivo")
    if not all(col in df2.columns for col in ['id','status']):
        raise HTTPException(status_code=400, detail="Columnas faltantes en el archivo")
    if not all(col in df3.columns for col in ['id','nombre']):
        raise HTTPException(status_code=400, detail="Columnas faltantes en el archivo")

    df1["fecha_creacion"] = pd.to_datetime(df1["fecha_creacion"], errors='coerce')
    df1["fecha_termino"] = pd.to_datetime(df1["fecha_termino"], errors='coerce')
    
    bulk_insert(df2, 'flow_states', db)
    bulk_insert(df3, 'company',db)
    bulk_insert(df1, 'executions',db)

    return {"message": "Datos cargados exitosamente"}