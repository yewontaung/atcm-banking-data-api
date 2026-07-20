from typing import Optional, cast

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.configs import auth
from app.data import database
from app.dtos.inputs import MemberForm
from app.dtos.outputs import MemberListItem, ModificationResult
from app.dtos.searches import MemberSearch
from app.services import accounts, members
from app.utils.managers.security import SecurityContext


router = APIRouter(prefix="/members")

@router.get("/", response_model=list[MemberListItem])
@auth.authenticated
def index(
    search:MemberSearch=Depends(),
    session:Session = Depends(database.get_session)):
    return members.search(search, SecurityContext.get_user().user_id, session)

@router.get("/{member_id}")
@auth.authenticated
def detail(member_id:int, session:Session = Depends(database.get_session)):
    return accounts.profile(member_id, session)

@router.post("/", response_model=ModificationResult[int])
@auth.has_roles("Admin")
def save(form:MemberForm, session:Session = Depends(database.get_session)):
    return members.save(form, SecurityContext.get_user().user_id, session)

@router.put("/{member_id}")
@auth.has_roles("Admin")
def update(member_id:int, form:MemberForm, session:Session = Depends(database.get_session)):
    return members.update(member_id, form, session)