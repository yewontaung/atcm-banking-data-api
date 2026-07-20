from typing import Literal, TypeVar

from sqlalchemy import Select
from sqlmodel import col, or_

from app.data.enums import DatasetType, MemberRole
from app.data.models import Account, Dataset, DatasetIntent, Intent
from app.utils.basedto import BaseDto

S = TypeVar("S", bound=Select)

class MemberSearch(BaseDto):
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
    
class DatasetSearch(BaseDto):
    status:Literal["pending", "approved", None] = None
    strategy:Literal["intent", "collector", "command", None] = None
    dataset_type:DatasetType | None = None
    keyword:str | None = None

    def where(self, select:S) -> S:
        if self.status:
            select = select.where(Dataset.approved == (self.status == "approved"))
        if self.dataset_type:
            select = select.where(Dataset.dataset_type == self.dataset_type)
        if self.strategy and self.keyword:
            match self.strategy:
                case "intent":select = (
                    select.outerjoin(DatasetIntent, DatasetIntent.dataset_id == Dataset.dataset_id)
                        .outerjoin(Intent, DatasetIntent.intent_id == Intent.intent_id)
                        .where(col(Intent.label).ilike(f"{self.keyword}%"))
                )
                case "command":select = select.where(col(Dataset.command).ilike(f"{self.keyword}%"))
                case "collector":select = select.where(col(Account.name).ilike(f"{self.keyword}%"))
        return select
