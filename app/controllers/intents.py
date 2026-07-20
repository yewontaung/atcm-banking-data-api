from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.configs import auth
from app.data.database import get_session
from app.dtos.inputs import IntentEditForm, IntentForm
from app.dtos.outputs import IntentListItem, ModificationResult
from app.services import intents
from app.utils.managers.security import SecurityContext


router = APIRouter(prefix="/intents")

@router.get("/", response_model=list[IntentListItem])
@auth.authenticated
def search(q:str | None = Query(None), session:Session = Depends(get_session)):
    return intents.search(q, session)

@router.get("/{intent_id}")
def detail():...

@router.post("/", response_model=ModificationResult[int])
@auth.has_roles("Admin")
def save(form:IntentForm, session:Session = Depends(get_session)):
    return intents.save(form, SecurityContext.get_user().user_id, session)

@router.delete("/{intent_id}", response_model=ModificationResult[int])
@auth.has_roles("Admin")
def delete(intent_id:int, session:Session = Depends(get_session)):
    return intents.delete(intent_id, session)

@router.put("/{intent_id}", response_model=ModificationResult[int])
@auth.has_roles("Admin")
def edit(intent_id:int, form:IntentEditForm, session:Session = Depends(get_session)):
    return intents.edit(intent_id, form, session)