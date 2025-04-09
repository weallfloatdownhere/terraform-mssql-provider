from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, select, Column, Integer, String, Table, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.sql import text, quoted_name

# MSSQL Database Connection Details
DATABASE_URL = "mssql+pyodbc://@localhost\\SQLEXPRESS/testing?driver=ODBC+Driver+17+for+SQL+Server"

# Create the database engine
engine = create_engine(DATABASE_URL, echo=True)

# Session local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base Model
Base = declarative_base()

# FastAPI App
# app = FastAPI()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def add_user(group_name: str):
    db = SessionLocal()
    try:
        db.execute(text(f"CREATE LOGIN {quoted_name(group_name, False)} WITH PASSWORD = '{group_name}'"))                       
        db.commit()
    except Exception as e:
        print(f"ERROR {e}")
    
    try:
        db.execute(text(f"CREATE USER {quoted_name(group_name, False)} FOR LOGIN {group_name}"))                        
        db.commit()
    except Exception as e:
        print(f"ERROR {e}")


def select_user(group_name: str):
    db = SessionLocal()
    metadata = MetaData()

    sql_logins = Table(
        "sql_logins", metadata,
        Column("principal_id", Integer),  
        Column("sid", String),  
        Column("name", String),  
        Column("type", String),  
        Column("is_disabled", Integer),  
        schema="sys"
    )

    query = select(sql_logins).where(sql_logins.c.name == "ADSQLGroup3")
    result = db.execute(query)
    
    for row in result:
        print(row)

USERNAME = "testing1"
#add_user(USERNAME)
select_user(USERNAME)

## User Model
#class User(Base):
#    __tablename__ = "users"
#    
#    id = Column(Integer, primary_key=True, index=True)
#    name = Column(String)
#    email = Column(String)
#
#
## Create database tables
#Base.metadata.create_all(bind=engine)
#
## Routes
#@app.post("/add_group")
#def create_user(group: str, db: Session = Depends(get_db)):
#    add_user(group, db)
#
#@app.post("/users/")
#def create_user(name: str, email: str, db: Session = Depends(get_db)):
#    new_user = User(name=name, email=email)
#    db.add(new_user)
#    db.commit()
#    db.refresh(new_user)
#    return new_user
#
#@app.get("/users/{user_id}")
#def read_user(user_id: int, db: Session = Depends(get_db)):
#    user = db.query(User).filter(User.id == user_id).first()
#    if user is None:
#        raise HTTPException(status_code=404, detail="User not found")
#    return user