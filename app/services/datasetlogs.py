from sqlalchemy.orm import selectinload
from sqlmodel import Session, func, select

from app.data.models import Account, DatasetModificationLog
from app.dtos.outputs import DatasetModificationLogListItem
from app.utils.paginations import PaginationResult


def search(page:int, size:int, session:Session) -> PaginationResult[DatasetModificationLogListItem]:
    query = select(
        DatasetModificationLog,
        Account).select_from(DatasetModificationLog).join(
            Account, Account.account_id == DatasetModificationLog.account_id
        ).limit(size).offset((page - 1) * size)

    count = select(func.count(DatasetModificationLog.log_id))

    result = session.exec(query).all()
    total = session.exec(count).one_or_none()
    
    items = [DatasetModificationLogListItem(
        log_id=log.log_id,
        dataset_id=log.dataset_id,
        account_id=log.account_id,
        name=account.name,
        account_email=account.account_email,
        profile_url=account.profile_url,
        account_role=account.role,
        modification_type=log.modification_type,
        modified_at=log.created_at,
    ) for log, account in result]

    return PaginationResult(
        items=items,
        page=page,
        size=size,
        total=total or 0
    )