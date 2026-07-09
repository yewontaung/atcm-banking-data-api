from dataclasses import dataclass
from typing import Generic, TypeVar

from sqlmodel import col, select

from data.enums import MemberRole
from data.models import Account


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