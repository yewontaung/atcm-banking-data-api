from datetime import datetime

from sqlalchemy import ForeignKeyConstraint
from sqlmodel import Field, Relationship, SQLModel

from app.data.enums import DatasetType, MemberRole


class Account(SQLModel, table=True):
    account_id:int | None = Field(primary_key=True, default=None)
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
    intent_id:int | None = Field(primary_key=True, default=None)
    label:str = Field(unique=True, nullable=False)
    description:str = Field(nullable=True, default="")
    created_at:datetime = Field()
    updated_at:datetime | None = Field(nullable=True)
    created_by:int = Field(foreign_key="account.account_id")
    ners:list[NER] = Relationship(link_model=NerIntentLink)

class Dataset(SQLModel, table=True):
    dataset_id:int | None = Field(primary_key=True, default=None)
    command:str = Field(nullable=False)
    dataset_type:DatasetType = Field(nullable=False)
    approved:bool = Field(nullable=False)
    member_id:int = Field(nullable=False)
    created_at:datetime = Field(nullable=True)
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
    datasetintent_id:int | None = Field(primary_key=True, default=None)
    intent_id:int = Field()
    dataset_id:int = Field()
    start_index:int = Field(nullable=False)
    end_index:int = Field(nullable=False)
    dataset:Dataset = Relationship(back_populates="intents")

    intent:Intent = Relationship()

    ners:list["DatasetIntentNer"] = Relationship(back_populates="datasetintent", sa_relationship_kwargs={
        "passive_deletes": True
    })

    __table_args__ = (
        ForeignKeyConstraint(
            ["intent_id"],
            ["intent.intent_id"],
            name="fk_datasetintent_intent"
        ),
        ForeignKeyConstraint(
            ["dataset_id"],
            ["dataset.dataset_id"],
            ondelete="CASCADE",
            name="fk_datasetintent_dataset"
        ),
    )

class DatasetIntentNer(SQLModel, table=True):
    datasetintentner_id:int | None = Field(primary_key=True, default=None)
    ner_id:int = Field()
    datasetintent_id:int = Field()
    start_index:int = Field(nullable=False)
    end_index:int = Field(nullable=False)

    ner:NER = Relationship()
    datasetintent:DatasetIntent = Relationship(back_populates="ners")

    __table_args__ = (
        ForeignKeyConstraint(
            ["ner_id"],
            ["ner.ner_id"],
            name="fk_datasetintentner_ner"
        ),
        ForeignKeyConstraint(
            ["datasetintent_id"],
            ["datasetintent.datasetintent_id"],
            name="fk_datasetintentner_datasetintent",
            ondelete="CASCADE"
        ),
    )
