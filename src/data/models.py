from datetime import datetime

from sqlmodel import Field, SQLModel

from data.enums import MemberRole


class Account(SQLModel, table=True):
    account_id:int = Field(primary_key=True, default=None)
    account_email:str = Field(unique=True, nullable=False)
    name:str = Field(nullable=False)
    role:MemberRole = Field(nullable=False)
    hashed_password:str = Field(nullable=False)
    profile_url:str = Field(nullable=True)

    created_at:datetime = Field()
    updated_at:datetime = Field(nullable=True)