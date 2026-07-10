from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from configs import auth
from data.database import get_session
from dtos.inputs import IntentForm
from dtos.outputs import IntentListItem, ModificationResult
from services import intents
from utils.managers.security import SecurityContext


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