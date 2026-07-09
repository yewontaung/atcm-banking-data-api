from dataclasses import dataclass
from datetime import datetime
from typing import Generic, TypeVar

from sqlmodel import col, func, select

from data.enums import MemberRole
from data.models import NER, Account, Intent, NerIntentLink


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
