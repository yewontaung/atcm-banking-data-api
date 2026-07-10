from datetime import datetime, timezone

from pydantic import BaseModel, EmailStr, Field

from data.enums import DatasetType
from data.models import Dataset


class MemberForm(BaseModel):
    name:str = Field()
    role:str = Field()
    member_email:EmailStr

class SignInForm(BaseModel):
    account_email:EmailStr
    password:str = Field(min_length=6)

class NerForm(BaseModel):
    label:str = Field()

class IntentForm(BaseModel):
    label:str
    description:str
    ners:list[int]

class DatasetIntentNerItem(BaseModel):
    ner_id:int
    label:str
    start_index:int
    end_index:int

class DatasetIntentItem(BaseModel):
    intent_id:int
    label:str
    start_index:int
    end_index:int
    ners:list[DatasetIntentNerItem]

class DatasetForm(BaseModel):
    command:str
    dataset_type:DatasetType
    intents:list[DatasetIntentItem]

    def dataset(self, user_id:int) -> Dataset:
        return Dataset(
            command=self.command,
            dataset_type=self.dataset_type,
            approved=False,
            member_id=int(user_id),
            updated_at=datetime.now(tz=timezone.utc),
        )
    
class PasswordForm(BaseModel):
    old_password:str = Field(min_length=6)
    new_password:str = Field(min_length=6)
    confirm_password:str = Field(min_length=6)

    @property
    def is_valid(self) -> bool:
        return self.new_password == self.confirm_password