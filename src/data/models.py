from datetime import datetime

from sqlmodel import Field, ForeignKey, Relationship, SQLModel

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

class NerIntentLink(SQLModel, table=True):
    ner_id:int = Field(primary_key=True, foreign_key="ner.ner_id")
    intent_id:int = Field(primary_key=True, foreign_key="intent.intent_id")

class NER(SQLModel, table=True):
    ner_id:int = Field(primary_key=True, default=None)
    label:str = Field(unique=True, nullable=False)
    created_at:datetime = Field()
    updated_at:datetime = Field(nullable=True)
    created_by:int = Field(foreign_key="account.account_id")

class Intent(SQLModel, table=True):
    intent_id:int = Field(primary_key=True, default=None)
    label:str = Field(unique=True, nullable=False)
    created_at:datetime = Field()
    updated_at:datetime = Field(nullable=False)
    created_by:int = Field(foreign_key="account.account_id")
    ners:list[NER] = Relationship(link_model=NerIntentLink)
