from typing import Literal, TypeVar

from pydantic import BaseModel
from sqlalchemy import Select
from sqlmodel import col, or_

from data.enums import MemberRole
from data.models import Account, Dataset, DatasetIntent, Intent

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
    
class DatasetSearch(BaseModel):
    status:Literal["pending", "approved", None] = None
    strategy:Literal["intent", "collector", "command", None] = None
    keyword:str | None = None

    def where(self, select:S) -> S:
        if self.status:
            select = select.where(Dataset.approved == (self.status == "approved"))
        if self.strategy and self.keyword:
            match self.strategy:
                case "intent":select = (
                    select.join(DatasetIntent, DatasetIntent.dataset_id == Dataset.dataset_id)
                        .join(Intent, DatasetIntent.intent_id == Intent.intent_id)
                        .where(col(Intent.label).ilike(f"{self.keyword}%"))
                )
                case "command":select = select.where(col(Dataset.command).ilike(f"{self.keyword}%"))
                case "collector":select = select.where(col(Account.name).ilike(f"{self.keyword}%"))
        return select
