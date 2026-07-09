from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from configs import auth
from data.database import get_session
from dtos.outputs import DatasetListItem
from dtos.searches import DatasetSearch
from services import datasets
from utils.paginations import PaginationResult


router = APIRouter(prefix="/datasets")

@router.get("/", response_model=PaginationResult[DatasetListItem])
@auth.authenticated
def search(
    page:int = Query(10),
    size:int = Query(10),
    search:DatasetSearch = Depends(), 
    session:Session = Depends(get_session)):
    return datasets.search(search, page, size, session)