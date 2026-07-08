from dataclasses import dataclass
from typing import Generic, TypeVar

from data.enums import MemberRole


@dataclass(frozen=True)
class MemberListItem:
    member_id:int
    member_name:str
    member_email:str
    role:MemberRole
    datasets:int


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