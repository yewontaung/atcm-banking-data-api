from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, func, select

from app.configs import evm
from app.data.database import safe_call
from app.data.enums import DatasetType, ModificationType
from app.data.models import Account, Dataset, DatasetIntent, DatasetIntentNer
from app.dtos.events import DatasetModificationEvent
from app.dtos.inputs import DatasetForm
from app.dtos.outputs import DatasetAnalysis, DatasetDetail, DatasetDetailIntent, DatasetDetailResult, DatasetInfo, DatasetListItem, ModificationResult, NextDatasetResult
from app.dtos.searches import DatasetSearch
from app.utils.exceptions import AppBusinessException
from app.utils.paginations import PaginationResult


def search(search:DatasetSearch, page:int, size:int, session:Session) -> PaginationResult[DatasetListItem]:
    sql = search.where(DatasetListItem.select()).where(Dataset.deleted == False).limit(size).offset((page - 1) * size)
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
    result = session.exec(DatasetListItem.select().where(Dataset.deleted == True).limit(size).offset((page - 1) * size)).all()
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
    if dataset.deleted:
        raise AppBusinessException("Cannot approved dataset from bin.")
    dataset.approved = True
    session.add(dataset)
    session.commit()

    event = DatasetModificationEvent(
        dataset_id=dataset_id,
        account_id=int(user_id),
        modification_type=ModificationType.Approve,
    )

    evm.publish(event=event)

    return ModificationResult(result_data=dataset.dataset_id)

def save(form:DatasetForm, user_id:str, session:Session) -> ModificationResult[int]:
    try:
        dataset = form.dataset(user_id)

        for intent in form.intents:
            intent = DatasetIntent(
                intent_id=intent.intent_id, 
                start_index=intent.start_index,
                end_index=intent.end_index,
                ners=[DatasetIntentNer(
                    ner_id=ner.ner_id, 
                    start_index=ner.start_index,
                    end_index=ner.end_index,
                ) for ner in intent.ners]
            )
        
            dataset.intents.append(intent)
        
        session.add(dataset)
        session.commit()

        return ModificationResult(result_data=dataset.dataset_id)
    except IntegrityError as e:
        print(str(e))
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
    dataset = safe_call(
        session.get(Dataset, dataset_id), 
        "Dataset", 
        "dataset_id", 
        dataset_id)
    
    session.delete(dataset)
    session.commit()
    return ModificationResult(result_data=dataset_id)

def find_by_id(dataset_id:int, session:Session) -> DatasetDetailResult:
    
    dataset = session.exec(
    select(Dataset).options(
        selectinload(Dataset.member),
        selectinload(Dataset.intents)
            .selectinload(DatasetIntent.intent),
        selectinload(Dataset.intents)
            .selectinload(DatasetIntent.ners)
            .selectinload(DatasetIntentNer.ner),
    ).where(Dataset.dataset_id == dataset_id)).first()
    
    dataset = safe_call(dataset, "Dataset", "dataset_id", dataset_id)

    # detail = DatasetDetail(
    #     dataset_id=dataset.dataset_id,
    #     command=dataset.command,
    #     intents=[DatasetDetailIntent.from_(item) for item in dataset.intents],
    #     alignments=[DatasetIntentNerAlignment.from_(ner, item.intent_id) 
    #                 for item in dataset.intents 
    #                 for ner in item.ners
    #             ]
    # )

    detail = DatasetDetail(
        dataset_id=dataset.dataset_id,
        text=dataset.command,
        intents=[DatasetDetailIntent.from_(item) for item in dataset.intents]
    )

    return DatasetDetailResult(
        dataset=detail,
        info=DatasetInfo(
            dataset_id=dataset.dataset_id,
            member_id=dataset.member_id,
            member_name=dataset.member.name,
            member_role=dataset.member.role,
            dataset_type=dataset.dataset_type,
            last_updated=dataset.updated_at,
            approved=dataset.approved,
            deleted=dataset.deleted,
        )
    )

def restore(dataset_id:int, session:Session) -> ModificationResult[int]:
    dataset = safe_call(session.get(Dataset, dataset_id), "Dataset", "dataset_id", dataset_id)
    dataset.deleted = False
    session.add(dataset)
    session.commit()
    return ModificationResult(result_data=dataset.dataset_id)

def export(dataset_type:DatasetType, session:Session) -> list[DatasetDetail]:
    datasets = session.exec(select(Dataset).options(
        selectinload(Dataset.intents)
            .selectinload(DatasetIntent.intent),
        selectinload(Dataset.intents)
            .selectinload(DatasetIntent.ners)
            .selectinload(DatasetIntentNer.ner),
        selectinload(Dataset.member)
    ).where(Dataset.dataset_type == dataset_type, Dataset.deleted != True, Dataset.approved == True)).all()

    result:list[DatasetDetail] = []

    # for dataset in datasets:
    #     detail = DatasetDetail(
    #         dataset_id=dataset.dataset_id,
    #         command=dataset.command,
    #         intents=[DatasetDetailIntent.from_(item) for item in dataset.intents],
    #         alignments=[DatasetIntentNerAlignment.from_(ner, item.intent_id) 
    #                     for item in dataset.intents 
    #                     for ner in item.ners
    #                 ]
    #     )

    for dataset in datasets:
        detail = DatasetDetail(
            dataset_id=dataset.dataset_id,
            text=dataset.command,
            intents=[DatasetDetailIntent.from_(item) for item in dataset.intents]
        )

        result.append(detail)
    
    return result

def analysis(session:Session) -> DatasetAnalysis:
    DATASETS = (select(
        Dataset.dataset_type,
        func.count(Dataset.dataset_id))
    .where(
        Dataset.deleted == False, 
        Dataset.approved == True
    ).group_by(Dataset.dataset_type))

    total_datasets = session.exec(DATASETS).all()
    
    training_datasets = 0
    validation_datasets = 0
    testing_datasets = 0

    for dataset_type, datasets in total_datasets:
        match dataset_type:
            case DatasetType.Training: training_datasets += datasets
            case DatasetType.Validation: validation_datasets += datasets
            case DatasetType.Testing: testing_datasets += datasets

    return DatasetAnalysis(
        training_datasets=training_datasets,
        validation_datasets=validation_datasets,
        testing_datasets=testing_datasets,
    )

def update(dataset_id:int, update:DatasetDetail, user_id:str, session:Session) -> ModificationResult[int]:

    if dataset_id != update.dataset_id:
        raise AppBusinessException("Invalid dataset.")

    dataset = safe_call(session.get(Dataset, dataset_id), "Dataset", "dataset_id", dataset_id)
    account = safe_call(session.get(Account, user_id), "Account", "user_id", user_id)

    dataset.command = update.text
    old_intents = dataset.intents

    def find_old_intent(datasetintent_id:int) -> DatasetIntent:
        for old_intent in old_intents:
            if old_intent.datasetintent_id != datasetintent_id:
                continue
            else:
                return old_intent

    def find_old_entity(datasetintentner_id:int, old_entities:list[DatasetIntentNer]) -> DatasetIntentNer:
        for old_entity in old_entities:
            if old_entity.datasetintentner_id != datasetintentner_id:
                continue
            else:
                return old_entity

    for item in update.intents:
        old_intent = find_old_intent(item.datasetintent_id)
        if not old_intent:
            continue

        old_intent.start_index = item.start_index
        old_intent.end_index = item.end_index

        for entity in item.entities:
            old_entity = find_old_entity(entity.datasetintentner_id, old_intent.ners)
            if not old_entity:
                continue
            old_entity.start_index = entity.start_index
            old_entity.end_index = entity.end_index

    session.commit()

    event = DatasetModificationEvent(
        dataset_id=dataset.dataset_id,
        account_id=account.account_id,
        modification_type=ModificationType.Edit,
    )

    evm.publish(event=event)

    return ModificationResult(result_data=dataset_id)

def next_dataset(dataset_id:int, session:Session) -> NextDatasetResult:
    query = select(Dataset.dataset_id).where(Dataset.dataset_id != dataset_id, Dataset.approved == False, Dataset.deleted == False).order_by(func.random()).limit(1)
    dataset_id = session.exec(query).one_or_none()
    return NextDatasetResult(next_dataset_id=dataset_id)