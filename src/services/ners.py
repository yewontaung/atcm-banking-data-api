from datetime import datetime, timezone

from sqlmodel import Session, col, desc, select

from data.database import safe_call
from data.models import NER
from dtos.inputs import NerForm
from dtos.outputs import ModificationResult, NerListItem
from utils.exceptions import AppBusinessException

def search(q:str | None, session:Session) -> list[NerListItem]:
    sql = NerListItem.select().order_by(desc(col(NER.ner_id)))
    if q:
        sql = sql.where(col(NER.label).ilike(f"{q}%"))
    result = session.exec(statement=sql).all()

    return [NerListItem(item.ner_id, item.label, item.updated_at or item.created_at, intent) for item, intent in result]

def save(form:NerForm, user_id:str, session:Session) -> ModificationResult[int]:
    if session.exec(select(NER).where(NER.label == form.label)).one_or_none():
        raise AppBusinessException(f"NER with label:{form.label} already exists.")
    ner = NER(label=form.label, created_at=datetime.now(tz=timezone.utc), created_by=int(user_id))
    session.add(ner)
    session.commit()
    session.refresh(ner)
    return ModificationResult(ner.ner_id)