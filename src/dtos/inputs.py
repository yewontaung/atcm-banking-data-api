from pydantic import BaseModel, EmailStr, Field

from data.enums import DatasetType


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