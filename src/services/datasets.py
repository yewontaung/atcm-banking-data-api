from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from data.models import Dataset, DatasetIntent, DatasetIntentNer, Intent
from dtos.inputs import DatasetForm
from dtos.outputs import DatasetListItem, ModificationResult
from dtos.searches import DatasetSearch
from utils.exceptions import AppBusinessException
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
    try:
        dataset = Dataset(
            command=form.command,
            dataset_type=form.dataset_type,
            approved=False,
            member_id=int(user_id),
            updated_at=datetime.now(tz=timezone.utc),
        )
        session.add(dataset)
        session.flush([dataset])

        intents = [DatasetIntent(
            intent_id=intent.intent_id, 
            dataset_id=dataset.dataset_id,
            start_index=intent.start_index,
            end_index=intent.end_index,
            ners=[DatasetIntentNer(
                ner_id=ner.ner_id, 
                intent_id=intent.intent_id, 
                dataset_id=dataset.dataset_id,
                start_index=ner.start_index,
                end_index=ner.end_index) for ner in intent.ners]) 
            for intent in form.intents]
        
        session.add_all(intents)
        session.commit()

        return ModificationResult(dataset.dataset_id)
    except IntegrityError as e:
        raise AppBusinessException("Something went worng. Check input value again.")