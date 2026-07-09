from typing import TypeVar

from pydantic import BaseModel
from sqlalchemy import Select
from sqlmodel import col, or_

from data.enums import MemberRole
from data.models import Account

S = TypeVar("S", bound=Select)

class MemberSearch(BaseModel):
    role:MemberRole|None = None
    keyword:str|None = None

    def where(self, select:S) -> S:
        if self.role:
            select = select.where(Account.role == self.role)
        if self.keyword:
            select = select.where(
                    or_(col(Account.name).ilike(f"{self.keyword}%"),
                    or_(col(Account.account_email).ilike(f"{self.keyword}%")),
                )
            )
        return select