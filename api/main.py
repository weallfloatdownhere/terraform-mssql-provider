# https://learn.microsoft.com/en-us/sql/relational-databases/security/authentication-access/database-level-roles?view=sql-server-ver16

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, select, Column, Integer, String, Table, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.sql import text, quoted_name

# MSSQL Server
SERVER   = "localhost\\SQLEXPRESS"
# MSSQL Database
DATABASE = "testing"

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
def connect_to_database(server: str, database: str):
    # Create the database engine
    engine = create_engine(f"mssql+pyodbc://@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server", echo=True)
    # Initialize the Session local
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    # Return the session
    return SessionLocal

# Group exists function in sys.sql_logins
def group_exists_in_sql_logins(group_name: str, SessionLocal: Session):
    # Initialize session
    db = SessionLocal()
    # Query to select the group in the sql_logins table
    query = select(sql_logins).where(sql_logins.c.name == group_name)
    # Execute the query
    result = db.execute(query)
    # Return the result
    if len(result.all()) > 0: # the group already exists
        return 1
    else: # the group doesnt exists
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
    if len(result.all()) == 1: # the group already exists
        return 1
    else: # the group doesnt exists
        return 0

# Adding group the the sql_logins
def add_group_to_sql_logins(group_name: str, SessionLocal: Session):
    # Check if the group exists in sql_logins before adding it
    if group_exists_in_sql_logins(group_name, SessionLocal) <= 0:
        # Initialize session
        db = SessionLocal()
        # Add the user to the sql_logins
        try:
            db.execute(text(f"CREATE LOGIN {quoted_name(group_name, False)} WITH PASSWORD = '{group_name}'"))                       
            db.commit()
            return 0
        except Exception as e:
            db.close()
            print(f"ERROR {e}")
    else:
        return 1

# Adding group the the database_principals
# TODO: CREATE USER GROUPNAME FROM EXTERNAL PROVIDER
def add_group_to_database_principals(group_name: str, SessionLocal: Session):
    # Check if the group exists in database_principals before adding it
    if group_exists_in_the_database(group_name, SessionLocal) <= 0:
        # Initialize session
        db = SessionLocal()
        # Add the user to the sql_logins
        try:
            db.execute(text(f"CREATE USER {quoted_name(group_name, False)} FOR LOGIN {group_name}"))                          
            db.commit()
            return 0
        except Exception as e:
            db.close()
            print(f"ERROR {e}")
    else:
        return 1

def main():
    # Initialize database session
    session = connect_to_database(SERVER, DATABASE)
    # Add the group to sql_logins
    add_group_to_sql_logins("ADSQLGroup4", session)
    # Add the group to database_principals
    add_group_to_database_principals("ADSQLGroup4", session)
    

#SELECT roles.principal_id AS RolePrincipalID,
#    roles.name AS RolePrincipalName,
#    database_role_members.member_principal_id AS MemberPrincipalID,
#    members.name AS MemberPrincipalName
#FROM sys.database_role_members AS database_role_members
#INNER JOIN sys.database_principals AS roles
#    ON database_role_members.role_principal_id = roles.principal_id
#INNER JOIN sys.database_principals AS members
#    ON database_role_members.member_principal_id = members.principal_id
#WHERE members.name = 'testing1' AND roles.name = 'db_accessadmin'

main()

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