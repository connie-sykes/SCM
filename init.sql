CREATE DATABASE challenge;
USE challenge;

CREATE TABLE Flow_states(
    id int IDENTITY(1,1) PRIMARY KEY,
    status varchar(25) NOT NULL
);

CREATE TABLE Company(
    id int IDENTITY(1,1) PRIMARY KEY,
    nombre varchar(255) NOT NULL
);

CREATE TABLE Executions(
    id int IDENTITY(1,1) PRIMARY KEY, 
    fecha_creacion datetime NOT NULL,
    fecha_termino datetime NULL,
    start_dtm date NULL,
    end_dtm date NULL,
    company_id int FOREIGN KEY REFERENCES Company(id),
    estado varchar(25),
    status_id int FOREIGN KEY REFERENCES Flow_states(id)
);