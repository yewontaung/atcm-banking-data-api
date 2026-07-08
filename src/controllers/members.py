from typing import Optional

from fastapi import APIRouter, Depends, Query

from dtos.inputs import MemberForm
from dtos.outputs import MemberListItem
from dtos.searches import MemberSearch
from services import members


router = APIRouter(prefix="/members")

@router.get("/", response_model=list[MemberListItem])
def index(
    search:MemberSearch=Depends(),):
    return members.search(search)

@router.get("/{member_id}")
def detail(member_id:int):
    return members.profile(member_id)

@router.post("/")
def save(form:MemberForm):
    return members.save(form)

@router.put("/{member_id}/role")
def update(member_id:int):
    ...