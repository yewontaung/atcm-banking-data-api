from datetime import datetime, timezone

from sqlmodel import Session, desc, func, select

from data.database import safe_call
from data.enums import MemberRole
from data.models import Account, Dataset
from dtos.inputs import MemberForm
from dtos.outputs import MemberListItem, ModificationResult
from dtos.searches import MemberSearch
from utils import env
from utils.exceptions import AppBusinessException
from utils.singletons import hash_password


def search(search:MemberSearch, user_id:str, session:Session) -> list[MemberListItem]:
    
    sql = search.where(
        MemberListItem.select(Dataset).select_from(Account)
        .join(Dataset, Dataset.member_id == Account.account_id, isouter=True)
    ).order_by(desc(Account.account_id))
    result = session.execute(statement=sql).all()
    return [MemberListItem(**item._mapping) for item in result]

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
    return ModificationResult(result_data=account.account_id)

def update(member_id:int, form:MemberForm, session:Session) -> ModificationResult[int]:
    member = safe_call(session.get(Account, member_id), "Member", "member_id", member_id)
    if not form.is_valid(member):
        raise AppBusinessException("Cannot update same data.")
    if session.exec(select(func.count(Account.account_id)).where(Account.account_email == form.member_email, Account.account_id != member.account_id)).one_or_none():
        raise AppBusinessException(f"{form.member_email} already exists. Please use another email address.")
    
    member.account_email = form.member_email
    member.name = form.name
    member.role = form.role

    session.add(member)
    session.commit()

    return ModificationResult(result_data=member.account_id)