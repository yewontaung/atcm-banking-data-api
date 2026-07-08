from sqlmodel import SQLModel, Session, create_engine

from utils import env
from .models import *

engine = create_engine(url=env.get_env(env.DATABASE_URL), echo=True)

def create_tables():
    SQLModel.metadata.create_all(bind=engine)

def get_session():
    with Session(bind=engine) as session:
        yield session