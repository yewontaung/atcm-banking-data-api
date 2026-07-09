from sqlmodel import Session, col, func, select

from data.models import Dataset
from dtos.inputs import DatasetForm
from dtos.outputs import DatasetListItem, ModificationResult
from dtos.searches import DatasetSearch
from utils.paginations import PaginationResult


def search(search:DatasetSearch, page:int, size:int, session:Session) -> PaginationResult[DatasetListItem]:
    sql = search.where(DatasetListItem.select()).limit(size).offset(page - 1)
    result = session.exec(statement=sql).all()
    items = [DatasetListItem(
                dataset.dataset_id, dataset.command, 
                dataset.dataset_type, dataset.approved,
                dataset.member_id, member_name, dataset.updated_at
            ) for dataset, member_name in result]

    count = search.where(DatasetListItem.count())
    total = session.exec(count).one_or_none()

    return PaginationResult(items, page, size, total or 0)

def save(form:DatasetForm, user_id:str, session:Session) -> ModificationResult[int]:
    # validation
    # check intents

    # check ners for each intents
    return ModificationResult(1)