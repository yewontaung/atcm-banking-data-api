from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from configs import auth
from data.database import get_session
from dtos.inputs import NerForm
from dtos.outputs import ModificationResult
from services import ners
from utils.managers.security import SecurityContext


router = APIRouter(prefix="/ners")

@router.get("/")
@auth.authenticated
def search(q:str | None = Query(default=None), session:Session = Depends(get_session)):
    return ners.search(q, session)

@router.get("/{ner_id}")
def detail():...

@router.post("/", response_model=ModificationResult[int])
@auth.hasroles("Admin")
def save(form:NerForm, session:Session = Depends(get_session)):
    return ners.save(form, SecurityContext.get_user().userid, session)