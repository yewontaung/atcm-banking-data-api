from datetime import datetime, timezone

from sqlmodel import Session, col, select

from data.models import NER, Intent
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
            item.intent_id, item.label, 
            item.updated_at or item.created_at, 
            dataset,
            [ner.label for ner in item.ners]
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
    
    return ModificationResult(intent.intent_id)