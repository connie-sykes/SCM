from sqlmodel import create_engine, SQLModel, Session, VARCHAR, SQLModel, Column, Integer, String, Field
from datetime import datetime, date
from os import getenv
from dotenv import load_dotenv

load_dotenv()

user=getenv("user")
password=getenv("password")

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

class User(SQLModel, table=True):
    __tablename__ = 'users'
    id: int = Field(primary_key=True)
    username: str = Field(sa_column=Column("username", VARCHAR(50), unique=True))
    email: str | None= None
    hashed_password: str


SQLALCHEMY_URL = ("mssql+pyodbc://"+servername+"/"+db_name+"?driver="+driver)
db_engine = create_engine(SQLALCHEMY_URL)


#Test conexión base de datos
try:
    with Session(db_engine) as session:
        print(f"Conexión exitosa a la base de datos '{db_name}'.")
except Exception as e:
    print(f"Error al conectarse a la base de datos: {e}")


def get_session():
    with Session(db_engine) as session:
        yield session

