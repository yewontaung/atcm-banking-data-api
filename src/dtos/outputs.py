from dataclasses import dataclass
from datetime import datetime
from typing import Generic, TypeVar

from sqlmodel import col, desc, distinct, func, select

from data.enums import DatasetType, MemberRole
from data.models import NER, Account, Dataset, DatasetIntent, Intent, NerIntentLink


@dataclass(frozen=True)
class MemberListItem:
    member_id:int
    member_name:str
    member_email:str
    role:MemberRole
    datasets:int

    @classmethod
    def select(cls):
        return select(
            col(Account.account_id).label("member_id"),
            col(Account.name).label("member_name"),
            col(Account.account_email).label("member_email"),
            col(Account.role),
        )

@dataclass(frozen=True)
class NerListItem:
    ner_id:int
    label:str
    last_updated:datetime | None
    intents:int

    @classmethod
    def select(cls):
        return (
            select(
                NER,
                func.count(col(NerIntentLink.intent_id))
            ).select_from(NER)
            .outerjoin(NerIntentLink, NER.ner_id == NerIntentLink.ner_id)
            .group_by(NER.ner_id)
        )

@dataclass(frozen=True)
class IntentListItem:
    intent_id:int
    label:str
    last_updated:datetime
    dataset:int
    ners:list[str]

    @classmethod
    def select(cls):
        return (select(
            Intent,
            func.count(col(DatasetIntent.dataset_id))
        ).select_from(Intent)
        .outerjoin(DatasetIntent, Intent.intent_id == DatasetIntent.intent_id)
        .group_by(Intent.intent_id, Intent.label))

@dataclass(frozen=True)
class DatasetListItem:
    dataset_id:int
    command:str
    dataset_type:DatasetType
    approved:bool
    member_id:int
    member_name:str
    last_updated:datetime

    @classmethod
    def select(cls):
        return (
            select(Dataset, Account.name)
            .select_from(Dataset)
            .join(Account, Account.account_id == Dataset.member_id)
            .order_by(desc(Dataset.updated_at))
        )

    @classmethod
    def count(cls):
        return (
            select(func.count(distinct(Dataset.dataset_id)))
            .select_from(Dataset)
            .join(Account, Account.account_id == Dataset.member_id)
        )

ID = TypeVar("ID")

@dataclass(frozen=True)
class ModificationResult(Generic[ID]):
    result_id:ID


@dataclass(frozen=True)
class AuthResult:
    account_id:int
    account_name:str
    account_email:str
    account_role:str
    profile_url:str

    access_token:str
    access_type:str = "Bearer"

@dataclass(frozen=True)
class Profile:
    account_id:int
    account_name:str
    account_email:str
    account_role:str
    profile_url:str

    training_dataset:int
    validation_dataset:int
    testing_dataset:int
