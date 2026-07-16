from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from configs import auth
from data.database import get_session
from dtos.inputs import DatasetForm
from dtos.outputs import DatasetDetailResult, DatasetListItem, ModificationResult
from dtos.searches import DatasetSearch
from services import datasets
from utils.managers.security import SecurityContext
from utils.paginations import PaginationResult


router = APIRouter(prefix="/datasets")


@router.get("/", response_model=PaginationResult[DatasetListItem])
@auth.authenticated
def search(
    page:int = Query(1),
    size:int = Query(10),
    search:DatasetSearch = Depends(), 
    session:Session = Depends(get_session)):
    return datasets.search(search, page, size, session)

@router.post("/", response_model=ModificationResult[int])
@auth.authenticated
def save(form:DatasetForm, session:Session = Depends(get_session)):
    return datasets.save(form, SecurityContext.get_user().user_id, session)

@router.post("/jsons", response_model=ModificationResult[list[int]])
@auth.authenticated
def save_jsons(forms:list[DatasetForm], session:Session = Depends(get_session)):
    return datasets.save_jsons(forms, SecurityContext.get_user().user_id, session)

@router.get("/bin", response_model=PaginationResult[DatasetListItem])
@auth.has_roles("Admin")
def recycle_bin(
    page:int = Query(1),
    size:int = Query(10),
    session:Session = Depends(get_session)):
    return datasets.recycle_bin(page, size, session)

@router.delete("/bin/{dataset_id}")
@auth.has_roles("Admin")
def delete(dataset_id:int, session:Session = Depends(get_session)):
    return datasets.delete(dataset_id=dataset_id, session=session)

@router.put("/bin/restore/{dataset_id}")
@auth.has_roles("Admin")
def restore(dataset_id:int, session:Session = Depends(get_session)):
    return datasets.restore(dataset_id=dataset_id, session=session)

@router.get("/{dataset_id}", response_model=DatasetDetailResult)
@auth.authenticated
def detail(dataset_id:int, session:Session = Depends(get_session)):
    return datasets.find_by_id(dataset_id, session)

@router.delete("/{dataset_id}")
@auth.has_roles("Admin", "Supervisor")
def soft_delete(dataset_id:int, session:Session = Depends(get_session)):
    return datasets.soft_delete(dataset_id, session)

@router.put("/approve/{dataset_id}", response_model=ModificationResult[int])
@auth.has_roles("Admin", "Supervisor")
def approve(dataset_id:int, session:Session = Depends(get_session)):
    return datasets.approve(dataset_id=dataset_id, user_id=SecurityContext.get_user().user_id, session=session)
