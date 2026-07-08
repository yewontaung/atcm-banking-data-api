from pydantic import BaseModel

from data.enums import MemberRole


class MemberSearch(BaseModel):
    role:MemberRole|None = None
    keyword:str|None = None