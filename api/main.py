# https://learn.microsoft.com/en-us/sql/relational-databases/security/authentication-access/database-level-roles?view=sql-server-ver16

from fastapi        import FastAPI, Depends, HTTPException
from sqlalchemy     import create_engine, select, Column, Integer, String, Table, MetaData, alias, literal
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.sql import text, quoted_name
from pydantic       import BaseModel
from typing         import List

app = FastAPI()                                                                                               # FastAPI App

class GroupShema(BaseModel):
    MemberPrincipalName: str
    RolePrincipalName: str
    Server: str
    Database: str
    class Config:
        orm_mode = True

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
    Column("principal_id", Integer),
    schema="sys"
)

database_role_members = Table(
    "database_role_members", MetaData(),
    Column("member_principal_id", Integer),
    Column("role_principal_id", Integer), 
    schema="sys"
)

# Database connection function
def connect_to_database(server: str, database: str):
    engine = create_engine(f"mssql+pyodbc://@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server", echo=True) # Create the database engine
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)                                    # Initialize the Session local
    return SessionLocal                                                                                            # Return the session

# Group exists function in sys.sql_logins
def is_group_exists_in_sql_logins(group_name: str, SessionLocal: Session):
    db = SessionLocal()                                                                                            # Initialize session
    query = select(sql_logins).where(sql_logins.c.name == group_name)                                              # Query to select the group in the sql_logins table
    result = db.execute(query)                                                                                     # Execute the query
    if len(result.all()) > 0:                                                                                      # Return the result the group already exists
        return 1
    else:                                                                                                          # Return the result the group doesnt exists
        return 0

# Group exists function in sys.database_principals
def is_group_exists_in_the_database_principals(group_name: str, SessionLocal: Session):
    db = SessionLocal()                                                                                            # Initialize session
    query = select(database_principals).where(database_principals.c.name == group_name)                            # Query to select the group in the sql_logins table
    result = db.execute(query)                                                                                     # Execute the query
    if len(result.all()) > 0:                                                                                      # Return the result the group already exists
        return 1                                                                                                   # Return 1 if it already exists
    else:                                                                                                          # Return the result the group doesnt exists
        return 0                                                                                                   # Return 0 if it does not already exists

# Check if the role is already attributed to the specified group
def is_role_attributed(group_name: str, role_name: str, SessionLocal: Session):
    db      = SessionLocal()                                                                                       # Initialize session
    roles   = alias(database_principals, name="roles")                                                             # Initialize the aliase `roles`
    members = alias(database_principals, name="members")                                                           # Initialize the aliases `members`
    query = (                                                                                                      # Build the query
        select(
            roles.c.principal_id.label("RolePrincipalID"),
            roles.c.name.label("RolePrincipalName"),
            database_role_members.c.member_principal_id.label("MemberPrincipalID"),
            members.c.name.label("MemberPrincipalName"),
        )
        .join(database_role_members, database_role_members.c.role_principal_id == roles.c.principal_id)
        .join(members, database_role_members.c.member_principal_id == members.c.principal_id)
        .where(members.c.name == group_name)
        .where(roles.c.name == role_name)
    )
    result = db.execute(query)                                                                                     # Execute the query
    if len(result.all()) > 0:                                                                                      # Return the result the group already exists
        return 1                                                                                                   # Return 1 if the role is already attributed
    else:                                                                                                          # Return 0 the result the role is not already attributed
        return 0

def get_group_from_database(group_name: str, server: str, database: str, SessionLocal: Session):
    db      = SessionLocal()                                                                                       # Initialize session
    roles   = alias(database_principals, name="roles")                                                             # Initialize the aliase `roles`
    members = alias(database_principals, name="members")                                                           # Initialize the aliases `members`
    query = (                                                                                                      # Build the query
        select(
            roles.c.principal_id.label("RolePrincipalID"),
            roles.c.name.label("RolePrincipalName"),
            database_role_members.c.member_principal_id.label("MemberPrincipalID"),
            members.c.name.label("MemberPrincipalName"),
            literal(server).label("Server"),
            literal(database).label("Database")
        )
        .join(database_role_members, database_role_members.c.role_principal_id == roles.c.principal_id)
        .join(members, database_role_members.c.member_principal_id == members.c.principal_id)
        .where(members.c.name == group_name)
    )
    result = db.execute(query)                                                                                     # Execute the query
    return result.all()

# Adding group the the sql_logins
#def add_group_to_sql_logins(group_name: str, SessionLocal: Session):                                              # Check if the group exists in sql_logins before adding it
#    db = SessionLocal()                                                                                           # Initialize session
#    try:                                                                                                          # Try to add the user to the sql_logins
#        db.execute(text(f"CREATE LOGIN {quoted_name(group_name, False)} WITH PASSWORD = '{group_name}'"))         # Execute the query                       
#        db.commit()                                                                                               # Commit to database
#        return 0                                                                                                  # return 0 if the query as been succesfull
#    except Exception as e:
#        db.close()                                                                                                # Close the database connection i case of error
#        print(f"ERROR {e}")                                                                                       # Print the error
#        return 1                                                                                                  # return 1 if the query as not been succesfull

# Adding group the the database_principals
# TODO: CREATE USER GROUPNAME FROM EXTERNAL PROVIDER
def add_group_to_database_principals(group_name: str, SessionLocal: Session):           
    db = SessionLocal()                                                                                            # Initialize session
    try:                                                                                                           # Try to add the user to the sql_logins
        db.execute(text(f"CREATE USER {quoted_name(group_name, False)} FOR LOGIN {group_name}"))                   # Execute the query                         
        db.commit()                                                                                                # Commit to database  
        return 0                                                                                                   # return 0 if the query as been succesfull
    except Exception as e:
        db.close()                                                                                                 # Close the database connection i case of error
        print(f"ERROR {e}")                                                                                        # Print the error
        return 1                                                                                                   # return 1 if the query as not been succesfull

# Attribute role to the group (PUT)
def add_role_to_group(group_name: str, role_name: str, SessionLocal: Session):                                     # Check if the role is already attributed
    db = SessionLocal()                                                                                            # Initialize session
    try:                                                                                                           # Try to attribute the role
        db.execute(text(f"ALTER ROLE {role_name} ADD MEMBER {group_name}"))                                        # Execute the query                         
        db.commit()                                                                                                # Commit to database  
        return 0                                                                                                   # return 0 if the query as been succesfull
    except Exception as e:
        db.close()                                                                                                 # Close the database connection i case of error
        print(f"ERROR {e}")                                                                                        # Print the error
        return 1                                                                                                   # return 1 if the query as not been succesfull
        
# Unattribute role from the group (DELETE)
def delete_role_from_group(group_name: str, role_name: str, SessionLocal: Session):           
    if is_role_attributed(group_name, role_name, SessionLocal) > 0:                                                # Check if the role is already attributed
        db = SessionLocal()                                                                                        # Initialize session
        try:                                                                                                       # Try to attribute the role
            db.execute(text(f"ALTER ROLE {role_name} DROP MEMBER {group_name}"))                                   # Execute the query                         
            db.commit()                                                                                            # Commit to database  
            return 0                                                                                               # return 0 if the query as been succesfull
        except Exception as e:
            db.close()                                                                                             # Close the database connection i case of error
            print(f"ERROR {e}")                                                                                    # Print the error
            return 1                                                                                               # return 1 if the query as not been succesfull
    else:
        return "ALREADY EXISTS"

# Adding group the the database_principals
def delete_group_from_database_principals(group_name: str, SessionLocal: Session):           
    if is_group_exists_in_the_database_principals(group_name, SessionLocal) > 0:                                   # Check if the group exists in database_principals before adding it
        db = SessionLocal()                                                                                        # Initialize session
        try:                                                                                                       # Try to add the user to the sql_logins
            db.execute(text(f"DROP USER {quoted_name(group_name, False)} FROM EXTERNAL PROVIDER"))                 # Execute the query                         
            db.commit()                                                                                            # Commit to database
            return 0                                                                                               # return 0 if the query as been succesfull
        except Exception as e:
            db.close()                                                                                             # Close the database connection i case of error
            print(f"ERROR {e}")                                                                                    # Print the error
            return 1                                                                                               # return 1 if the query as not been succesfull
    else:
        return "ALREADY EXISTS"

def add_group_and_attribute_role(group_name: str, role_name: str, server: str, database: str, SessionLocal: Session):
    try:
        if is_group_exists_in_sql_logins(group_name, SessionLocal) <= 0:
            if is_group_exists_in_the_database_principals(group_name, SessionLocal) <= 0: add_group_to_database_principals(group_name, SessionLocal)
            if is_role_attributed(group_name, role_name, SessionLocal)              <= 0: add_role_to_group(group_name, role_name, SessionLocal)
            return { "MemberPrincipalName": group_name, "RolePrincipalName": role_name, "Server": server, "Database": database}
        else:
            return "ALREADY EXISTS"
    except Exception as e:
        return e

## Routes
@app.get("/server/{server}/database/{database}/group/{group_name}", response_model=List[GroupShema])
def get_group(server: str, database:str, group_name: str):
    session = connect_to_database(server, database)                                                               # Initialize database session
    return get_group_from_database(group_name, server, database, session)

@app.put("/server/{server}/database/{database}/group/{group_name}")
def update_group(server: str, database:str, group_name: str):
    # session = connect_to_database(server, database)                                                             # Initialize database session
    return("UPDATING")

@app.post("/server/{server}/database/{database}/group/{group_name}")
def create_group(server: str, database:str, group_name: str, role_name: str):
    session = connect_to_database(server, database)                                                               # Initialize database session
    return add_group_and_attribute_role(group_name, server, database, session)                                    # Add the group to database and attribute role

@app.delete("/server/{server}/database/{database}/group/{group_name}")
def delete_group(server: str, database:str, group_name: str):
    session = connect_to_database(server, database)                                                               # Initialize database session
    delete_group_from_database_principals(group_name, session)                                                    # Delete the group from the MSSQL


# SERVER     = "localhost\\SQLEXPRESS"                                                                            # MSSQL Server
# DATABASE   = "testing"                                                                                          # MSSQL Database
# GROUP_NAME = "ADSQLGroup4"
# IS_TEST    = False                                                                                              # Specify if its a test
# ADDING     = False                                                                                              # Specify if we adding group and role
# DELETE     = False                                                                                              # Specify if we deleting group and role
# 
# def test():                                                                                                     # Entrypoint function
#     session = connect_to_database(SERVER, DATABASE)                                                             # Initialize database session
#     if ADDING:
#         add_group_to_sql_logins(GROUP_NAME, session)                                                            # Add the group to sql_logins
#         add_group_to_database_principals(GROUP_NAME, session)                                                   # Add the group to database_principals
#         add_role_to_group(GROUP_NAME, "db_accessadmin", session)                                                # Attribute the role
#     if DELETE:
#         delete_role_from_group(GROUP_NAME, "db_accessadmin", session)                                           # Remove the role from the group
#         delete_group_from_database_principals(GROUP_NAME, session)                                              # Delete the group from the MSSQL
# 
# if IS_TEST:
#     test()