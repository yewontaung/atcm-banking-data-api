from pydantic import BaseModel, EmailStr, Field


class MemberForm(BaseModel):
    name:str = Field()
    role:str = Field()
    member_email:EmailStr

class SignInForm(BaseModel):
    account_email:EmailStr
    password:str = Field(min_length=6)

class NerForm(BaseModel):
    label:str = Field()