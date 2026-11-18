from sqlmodel import SQLModel, create_engine, Session


from dotenv import load_dotenv
import os
load_dotenv(dotenv_path=".env")

engine = create_engine(os.getenv("DB_URL" , "sqlite:///./test.db"), echo=True)


from . import models  

def create_db():
    SQLModel.metadata.create_all(engine) 
    


def get_session():
    with Session(engine) as session:
        yield session

if __name__ == "__main__":
    create_db()