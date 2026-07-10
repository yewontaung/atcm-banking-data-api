from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from configs import auth
from data.database import get_session
from dtos.inputs import DatasetForm
from dtos.outputs import DatasetListItem, ModificationResult
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
    return datasets.save(form, SecurityContext.get_user().userid, session)
    