from sqlmodel import create_engine, SQLModel, Session, text, SQLModel, Column, Integer, String, Field
from datetime import datetime, date

user = "sa"
password= "Catrine071014sql"
servername = f'{user}:{password}@localhost'
db_name = "challenge"
driver = "ODBC+Driver+17+for+SQL+Server"

class NotFoundError(Exception):
    pass

#Definicion de tablas
class Executions(SQLModel, table=True):
    __tablename__ = 'executions'
    id: int | None = Field(default=None, primary_key=True)
    fecha_creacion: datetime
    fecha_termino: datetime | None = None 
    start_dtm: date
    end_dtm: date
    company_id: int 
    estado: str
    status_id: int

class Flow_states(SQLModel, table=True):
    __tablename__ = 'flow_states'
    id: int | None = Field(default=None, primary_key=True)
    status: str


class Company(SQLModel, table=True):
    __tablename__ = 'company'
    id: int | None = Field(default=None, primary_key=True)
    nombre: str


SQLALCHEMY_URL = ("mssql+pyodbc://"+servername+"/"+db_name+"?driver="+driver)
db_engine = create_engine(SQLALCHEMY_URL)
#trusted_connection=yes&

#Test conexión base de datos
try:
    with Session(db_engine) as session:
        print(f"Conexión exitosa a la base de datos '{db_name}'.")
except Exception as e:
    print(f"Error al conectarse a la base de datos: {e}")


def get_session():
    with Session(db_engine) as session:
        yield session

