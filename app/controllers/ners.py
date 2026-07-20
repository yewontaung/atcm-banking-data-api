from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.configs import auth
from app.data.database import get_session
from app.dtos.inputs import NerForm
from app.dtos.outputs import ModificationResult
from app.services import ners
from app.utils.managers.security import SecurityContext


router = APIRouter(prefix="/ners")

@router.get("/")
@auth.authenticated
def search(q:str | None = Query(default=None), session:Session = Depends(get_session)):
    return ners.search(q, session)

@router.post("/", response_model=ModificationResult[int])
@auth.has_roles("Admin")
def save(form:NerForm, session:Session = Depends(get_session)):
    return ners.save(form, SecurityContext.get_user().user_id, session)

@router.delete("/{ner_id}")
@auth.has_roles("Admin")
def delete(ner_id:int, session:Session = Depends(get_session)):
    return ners.delete(ner_id, session)

@router.put("/{ner_id}")
@auth.has_roles("Admin")
def edit(ner_id:int, form:NerForm, session:Session = Depends(get_session)):
    return ners.update(ner_id, form, session)