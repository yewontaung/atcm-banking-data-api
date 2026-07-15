from datetime import datetime

from sqlalchemy import ForeignKeyConstraint
from sqlmodel import Field, Relationship, SQLModel

from data.enums import DatasetType, MemberRole


class Account(SQLModel, table=True):
    account_id:int = Field(primary_key=True, default=None)
    account_email:str = Field(unique=True, nullable=False)
    name:str = Field(nullable=False)
    role:MemberRole = Field(nullable=False)
    hashed_password:str = Field(nullable=False)
    profile_url:str = Field(nullable=True)

    created_at:datetime = Field()
    updated_at:datetime | None = Field(nullable=True)

    datasets:list["Dataset"] = Relationship(back_populates="member")

class NerIntentLink(SQLModel, table=True):
    ner_id:int = Field(primary_key=True, foreign_key="ner.ner_id")
    intent_id:int = Field(primary_key=True, foreign_key="intent.intent_id")

class NER(SQLModel, table=True):
    ner_id:int = Field(primary_key=True, default=None)
    label:str = Field(unique=True, nullable=False)
    created_at:datetime = Field()
    updated_at:datetime | None = Field(nullable=True)
    created_by:int = Field(foreign_key="account.account_id")

class Intent(SQLModel, table=True):
    intent_id:int = Field(primary_key=True, default=None)
    label:str = Field(unique=True, nullable=False)
    created_at:datetime = Field()
    updated_at:datetime | None = Field(nullable=True)
    created_by:int = Field(foreign_key="account.account_id")
    ners:list[NER] = Relationship(link_model=NerIntentLink)

class Dataset(SQLModel, table=True):
    dataset_id:int = Field(primary_key=True, default=None)
    command:str = Field(nullable=False)
    dataset_type:DatasetType = Field(nullable=False)
    approved:bool = Field(nullable=False)
    member_id:int = Field(nullable=False)
    updated_at:datetime = Field(nullable=False)
    deleted:bool = Field(nullable=False, default=False)

    member:Account = Relationship(back_populates="datasets")
    
    intents:list["DatasetIntent"] = Relationship(back_populates="dataset", sa_relationship_kwargs={
        "passive_deletes": True
    })

    __table_args__ = (
        ForeignKeyConstraint(
            ["member_id"],
            ["account.account_id"],
            name="fk_dataset_member"
        ),
    )

class DatasetIntent(SQLModel, table=True):
    intent_id:int = Field(primary_key=True, foreign_key="intent.intent_id")
    dataset_id:int = Field(primary_key=True)
    start_index:int = Field(nullable=False)
    end_index:int = Field(nullable=False)
    dataset:Dataset = Relationship(back_populates="intents")

    intent:Intent = Relationship()

    ners:list["DatasetIntentNer"] = Relationship(back_populates="intent", sa_relationship_kwargs={
        "passive_deletes": True
    })

    __table_args__ = (
        ForeignKeyConstraint(
            ["dataset_id"],
            ["dataset.dataset_id"],
            ondelete="CASCADE",
            name="datasetintent_dataset"
        ),
    )

class DatasetIntentNer(SQLModel, table=True):
    ner_id:int = Field(primary_key=True, foreign_key="ner.ner_id")
    intent_id:int = Field(primary_key=True)
    dataset_id:int = Field(primary_key=True)
    start_index:int = Field(nullable=False)
    end_index:int = Field(nullable=False)

    ner:NER = Relationship()
    intent:DatasetIntent = Relationship(back_populates="ners")

    __table_args__ = (
        ForeignKeyConstraint(
            ["intent_id", "dataset_id"],
            ["datasetintent.intent_id", "datasetintent.dataset_id"],
            ondelete="CASCADE",
            name="fk_datasetintentner_datasetintent_dataset"
        ),
    )
