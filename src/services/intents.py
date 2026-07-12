from datetime import datetime, timezone

from sqlmodel import Session, col, func, select

from data.database import safe_call
from data.models import NER, DatasetIntent, Intent
from dtos.inputs import IntentForm
from dtos.outputs import IntentListItem, ModificationResult
from utils.exceptions import AppBusinessException


def search(q:str | None, session:Session) -> list[IntentListItem]:
    sql = IntentListItem.select()
    if q:
        sql = sql.where(col(Intent.label).ilike(f"{q}%"))
    result = session.exec(statement=sql).all()
    return [
        IntentListItem(
            intent_id=item.intent_id, 
            label=item.label, 
            last_updated=item.updated_at or item.created_at, 
            dataset=dataset,
            ners=[ner.label for ner in item.ners]
        ) for item, dataset in result]

def save(form:IntentForm, user_id:str, session:Session):
    if session.exec(select(Intent).where(Intent.label == form.label)).one_or_none():
        raise AppBusinessException(f"Intent: {form.label} has already existed.")
    ners = session.exec(select(NER).where(col(NER.ner_id).in_(form.ners))).all()
    if len(ners) != len(form.ners):
        raise AppBusinessException(f"Invalid Named Entities.")
    intent = Intent(
        label=form.label,
        created_at=datetime.now(tz=timezone.utc),
        created_by=user_id,
        ners=ners
    )

    session.add(intent)
    session.commit()
    session.refresh(intent)
    
    return ModificationResult(result_data=intent.intent_id)

def delete(intent_id:int, session:Session) -> ModificationResult[int]:
    intent = safe_call(session.get(Intent, intent_id), "Intent", "intent_id", intent_id)
    count = select(func.count(DatasetIntent.intent_id)).select_from(DatasetIntent).where(DatasetIntent.intent_id == intent.intent_id)
    total = session.exec(count).one_or_none()
    if total:
        raise AppBusinessException(f"Intent with intent_id: {intent_id} cannot be deleted because it has {total} datasets.")
    session.delete(intent)
    session.commit()
    return ModificationResult(result_data=intent_id)