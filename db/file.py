from pydantic import BaseModel
from sqlmodel import SQLModel, select
from sqlmodel import Session
from fastapi import  HTTPException, Depends
from .database import Company, Session, get_session
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, APIRouter
import pandas as pd
from .database import Flow_states, Company, Executions


async def db_upload_excel(file: UploadFile = File(...), db: Session = Depends(get_session)):
    #Validacion del archivo
    if not file.filename.endswith('.xlsx'):
        return HTTPException(status_code=400, detail="El archivo debe ser Excel")
    
    xls = pd.ExcelFile(file.file)
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
    
    for index, row in df2.iterrows():
        db_flowstates = Flow_states(
            id=row["id"],
            status=row["status"]
            )
        db.add(db_flowstates)

    for index, row in df3.iterrows():
        db_company = Company(
            id=row["id"],
            nombre=row["nombre"]
        )
        db.add(db_company)
    db.commit()

    for index, row in df1.iterrows():
            db_execution = Executions(
            id=row["id"],
            fecha_creacion=row["fecha_creacion"],
            fecha_termino=row["fecha_termino"] if not pd.isnull(row["fecha_termino"]) else None,
            start_dtm=row["start_dtm"],
            end_dtm=row["end_dtm"],
            company_id=row["company_id"],
            estado=row["estado"],
            status_id=row["status_id"])
            db.add(db_execution)
    db.commit()

    return {"message": "Datos cargados exitosamente"}