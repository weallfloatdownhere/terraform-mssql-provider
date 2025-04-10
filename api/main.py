from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, select, Column, Integer, String, Table, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.sql import text, quoted_name

# Create the database engine
#engine = create_engine(DATABASE_URL, echo=True)
#
## Session local
#SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# FastAPI App
# app = FastAPI()

# TABLES
sql_logins = Table(
    "sql_logins", MetaData(),
    Column("principal_id", Integer),  
    Column("sid", String),  
    Column("name", String),  
    Column("type", String),  
    Column("is_disabled", Integer),  
    schema="sys"
)

database_principals = Table(
    "database_principals", MetaData(),
    Column("name", String),   
    Column("type", String),  
    Column("authentication_type", String),  
    schema="sys"
)

# Database connection function
def connect_to_database(CONNECTION_STRING: str):
    # Create the database engine
    engine = create_engine(CONNECTION_STRING, echo=True)
    # Initialize the Session local
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    # Return the session
    return SessionLocal

def get_db():
    # Create the database engine
    engine = create_engine(DATABASE_URL, echo=True)
    # Session local
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Group exists function in sys.sql_logins
def group_exists_in_sql_logins(group_name: str, SessionLocal: Session):
    # Initialize session
    db = SessionLocal()
    # Query to select the group in the sql_logins table
    query = select(sql_logins).where(sql_logins.c.name == group_name)
    # Execute the query
    result = db.execute(query)
    # Return the result
    if len(result.all()) == 1:                     # the group already exists
        print("EXISTS IN sys.sql_logins")
        return 1
    else:
        print("DOES NOT EXISTS IN sys.sql_logins") # the group doesnt exists
        return 0

# Group exists function in sys.database_principals
def group_exists_in_the_database(group_name: str, SessionLocal: Session):
    # Initialize session
    db = SessionLocal()
    # Query to select the group in the sql_logins table
    query = select(database_principals).where(database_principals.c.name == group_name)
    # Execute the query
    result = db.execute(query)
    # Return the result
    if len(result.all()) == 1:                              # the group already exists
        print("EXISTS IN sys.database_principals")
        return 1
    else:
        print("DOES NOT EXISTS IN sys.database_principals") # the group doesnt exists
        return 0


# MSSQL Database Connection Details
DATABASE_URL = "mssql+pyodbc://@localhost\\SQLEXPRESS/testing?driver=ODBC+Driver+17+for+SQL+Server"

session = connect_to_database(DATABASE_URL)

group_exists_in_sql_logins("ADSQLGroup4", session)
group_exists_in_the_database("ADSQLGroup4", session)

# Dependency to get DB session
#def get_db():
#    db = SessionLocal()
#    try:
#        yield db
#    finally:
#        db.close()
#
#def add_user(group_name: str):
#    db = SessionLocal()
#    try:
#        db.execute(text(f"CREATE LOGIN {quoted_name(group_name, False)} WITH PASSWORD = '{group_name}'"))                       
#        db.commit()
#    except Exception as e:
#        print(f"ERROR {e}")
#    
#    try:
#        db.execute(text(f"CREATE USER {quoted_name(group_name, False)} FOR LOGIN {group_name}"))                        
#        db.commit()
#    except Exception as e:
#        print(f"ERROR {e}")


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