from datetime import datetime, timezone

from pydantic import EmailStr, Field

from app.data.enums import DatasetType, MemberRole
from app.data.models import Account, Dataset
from app.utils.basedto import BaseDto


class MemberForm(BaseDto):
    name:str = Field()
    role:MemberRole = Field()
    member_email:EmailStr

    def is_valid(self, member:Account) -> bool:
        return (self.name != member.name or self.role != member.role or self.member_email != member.account_email)

class SignInForm(BaseDto):
    account_email:EmailStr
    password:str = Field(min_length=6)

class NerForm(BaseDto):
    label:str = Field()

class IntentForm(BaseDto):
    label:str
    description:str
    ners:list[int]

class IntentEditForm(BaseDto):
    label:str = Field()
    description:str = Field()

class DatasetIntentNerItem(BaseDto):
    ner_id:int
    label:str
    start_index:int
    end_index:int

class DatasetIntentItem(BaseDto):
    intent_id:int
    label:str
    start_index:int
    end_index:int
    ners:list[DatasetIntentNerItem]

class DatasetForm(BaseDto):
    command:str
    dataset_type:DatasetType
    intents:list[DatasetIntentItem]

    def dataset(self, user_id:int) -> Dataset:
        return Dataset(
            command=self.command,
            dataset_type=self.dataset_type,
            approved=False,
            member_id=int(user_id),
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )
    
class PasswordForm(BaseDto):
    old_password:str = Field(min_length=6)
    new_password:str = Field(min_length=6)
    confirm_password:str = Field(min_length=6)

    @property
    def is_valid(self) -> bool:
        return self.new_password == self.confirm_password