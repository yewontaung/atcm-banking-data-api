from sqlalchemy.exc import IntegrityError
from sqlmodel import Session
import sqlmodel

from data.database import safe_call
from data.models import Dataset, DatasetIntent, DatasetIntentNer
from dtos.inputs import DatasetForm
from dtos.outputs import DatasetListItem, ModificationResult
from dtos.searches import DatasetSearch
from utils.exceptions import AppBusinessException
from utils.paginations import PaginationResult


def search(search:DatasetSearch, page:int, size:int, session:Session) -> PaginationResult[DatasetListItem]:
    sql = search.where(DatasetListItem.select()).where(Dataset.deleted == False).limit(size).offset(page - 1)
    result = session.exec(statement=sql).all()
    items = [DatasetListItem(
                dataset_id=dataset.dataset_id, 
                command=dataset.command, 
                dataset_type=dataset.dataset_type, 
                approved=dataset.approved,
                member_id=dataset.member_id, 
                member_name=member_name, 
                last_updated=dataset.updated_at,
                deleted=dataset.deleted,
            ) for dataset, member_name in result]

    count = search.where(DatasetListItem.count()).where(Dataset.deleted == False)
    total = session.exec(count).one_or_none()
    return PaginationResult(items=items, page=page, size=size, total=total or 0)

def recycle_bin(page:int, size:int, session:Session) -> PaginationResult[DatasetListItem]:
    result = session.exec(DatasetListItem.select().where(Dataset.deleted == True)).all()
    items = [DatasetListItem(
                dataset_id=dataset.dataset_id, 
                command=dataset.command, 
                dataset_type=dataset.dataset_type, 
                approved=dataset.approved,
                member_id=dataset.member_id, 
                member_name=member_name, 
                last_updated=dataset.updated_at,
                deleted=dataset.deleted,
            ) for dataset, member_name in result]
    count = DatasetListItem.count().where(Dataset.deleted == True)
    total = session.exec(count).one_or_none()
    return PaginationResult(items=items, page=page, size=size, total=total or 0)

def approve(dataset_id:int, user_id:str, session:Session) -> ModificationResult[int]:
    dataset = safe_call(session.get(Dataset, dataset_id), "Dataset", "dataset_id", dataset_id)
    dataset.approved = True
    session.add(dataset)
    session.commit()
    return ModificationResult(result_data=dataset.dataset_id)

def save(form:DatasetForm, user_id:str, session:Session) -> ModificationResult[int]:
    try:
        dataset = form.dataset(user_id)
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

        return ModificationResult(result_data=dataset.dataset_id)
    except IntegrityError as e:
        raise AppBusinessException("Data validation failed. Check input value again.")
    
def save_jsons(forms:list[DatasetForm], user_id:int, session:Session) -> ModificationResult[list[int]]:
    try:
        result_id_list:list[int] = []
        for form in forms:
            dataset = form.dataset(user_id)
            session.add(dataset)
            session.flush([dataset])
            result_id_list.append(dataset.dataset_id)
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

        return ModificationResult(result_data=result_id_list)
    except IntegrityError as e:
        raise AppBusinessException("Data validation failed. Check input value again.")

def soft_delete(dataset_id:int, session:Session):
    dataset = safe_call(session.get(Dataset, dataset_id), "Dataset", "dataset_id", dataset_id)
    dataset.deleted = True
    session.add(dataset)
    session.commit()
    return ModificationResult(result_data=dataset_id)

def delete(dataset_id:int, session:Session):
    dataset = safe_call(session.get(Dataset, dataset_id), "Dataset", "dataset_id", dataset_id)
    session.exec(sqlmodel.delete(DatasetIntent))
    session.delete(dataset)
    session.commit()
    return ModificationResult(result_data=dataset_id)