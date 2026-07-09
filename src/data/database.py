from datetime import timezone
from typing import TypeVar

from sqlmodel import SQLModel, Session, col, create_engine, func, select

from utils import env
from utils.exceptions import ResourceNotFoundException
from utils.singletons import hash_password
from .models import *

engine = create_engine(url=env.DATABASE_URL, echo=True)

def create_tables():
    SQLModel.metadata.create_all(bind=engine)

def get_session():
    with Session(bind=engine) as session:
        yield session
        

T = TypeVar("T")

def safe_call(t:T | None, model:str, key:str, value:str) -> T:
    if t is None:raise ResourceNotFoundException(f"{model} with {key}: {value} is not found.")
    return t

def seed_admin():
    with Session(bind=engine) as session:
        count = session.exec(
                select(
                    func.count(col(Account.account_id))
                ).select_from(Account)).one()
        if count == 0:
            account = Account(
                account_email=env.ADMIN_EMAIL,
                hashed_password=hash_password(env.ADMIN_PASSWORD),
                name=env.ADMIN_NAME,
                role=MemberRole.Admin,
                created_at=datetime.now(tz=timezone.utc),
            )
            session.add(account)
            session.commit()