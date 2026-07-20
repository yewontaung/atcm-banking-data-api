from datetime import datetime, timezone

from sqlmodel import Session, col, desc, func, select

from app.data.database import safe_call
from app.data.models import NER, NerIntentLink
from app.dtos.inputs import NerForm
from app.dtos.outputs import ModificationResult, NerListItem
from app.utils.exceptions import AppBusinessException

def search(q:str | None, session:Session) -> list[NerListItem]:
    sql = NerListItem.select().order_by(desc(col(NER.ner_id)))
    if q:
        sql = sql.where(col(NER.label).ilike(f"{q}%"))
    result = session.exec(statement=sql).all()

    return [NerListItem(
        ner_id=item.ner_id, 
        label=item.label, 
        last_updated=item.updated_at or item.created_at, 
        intents=intents) for item, intents in result]

def save(form:NerForm, user_id:str, session:Session) -> ModificationResult[int]:
    if session.exec(select(NER).where(NER.label == form.label)).one_or_none():
        raise AppBusinessException(f"NER with label: {form.label} has already existed.")
    ner = NER(label=form.label, created_at=datetime.now(tz=timezone.utc), created_by=int(user_id))
    session.add(ner)
    session.commit()
    session.refresh(ner)
    return ModificationResult(result_data=ner.ner_id)

def delete(ner_id:int, session:Session) -> ModificationResult[int]:
    ner = safe_call(session.get(NER, ner_id), "Named Entity", "ner_id", ner_id)
    total = session.exec(select(
        func.count(NerIntentLink.ner_id)
    ).select_from(NerIntentLink).where(NerIntentLink.ner_id == ner.ner_id)).one_or_none()

    if total:
        raise AppBusinessException(f"Ner cannot be deleted because it has {total} datasets.")
    
    session.delete(ner)
    session.commit()
    return ModificationResult(result_data=ner_id)

def update(ner_id:int, form:NerForm, session:Session) -> ModificationResult[int]:
    ner = safe_call(session.get(NER, ner_id), "Named Entity", "ner_id", ner_id)
    ner.label = form.label
    session.add(ner)
    session.commit()
    return ModificationResult(result_data=ner.ner_id)
