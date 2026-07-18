from typing import Optional, cast

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from configs import auth
from data import database
from dtos.inputs import MemberForm
from dtos.outputs import MemberListItem, ModificationResult
from dtos.searches import MemberSearch
from services import accounts, members
from utils.managers.security import SecurityContext


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