from datetime import datetime, timezone

from sqlmodel import Session, desc, select

from data.enums import MemberRole
from data.models import Account
from dtos.inputs import MemberForm
from dtos.outputs import MemberListItem, ModificationResult
from dtos.searches import MemberSearch
from utils import env
from utils.exceptions import AppBusinessException
from utils.singletons import hash_password


def search(search:MemberSearch, user_id:str, session:Session) -> list[MemberListItem]:
    
    sql = search.where(MemberListItem.select()).order_by(desc(Account.account_id))
    result = session.exec(statement=sql).all()
    return [MemberListItem(*item, 0) for item in result]

def profile(member_id:int):...

def save(form:MemberForm, user_id:str, session:Session)-> ModificationResult[int]:
    if session.exec(select(Account).where(Account.account_email == form.member_email)).one_or_none() is not None:
        raise AppBusinessException(f"Member with email: {form.member_email} has already existed.")
    account = Account(
        account_email=form.member_email,
        role=MemberRole(form.role),
        created_at=datetime.now(tz=timezone.utc),
        hashed_password=hash_password(env.DEFAULT_PASSWORD),
        name=form.name,
    )
    session.add(account)
    session.commit()
    session.refresh(account)
    return ModificationResult(account.account_id)