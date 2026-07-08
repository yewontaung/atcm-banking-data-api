from dtos.inputs import MemberForm
from dtos.outputs import MemberListItem, ModificationResult
from dtos.searches import MemberSearch


def search(search:MemberSearch) -> list[MemberListItem]:...

def profile(member_id:int):...

def save(form:MemberForm) -> ModificationResult[int]:
    return ...