from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def create_database_engine(username, password, host, database):
    connection_string = f"mysql+pymysql://{username}:{password}@{host}/{database}"
    engine = create_engine(connection_string, echo=True)
    return engine

def create_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()