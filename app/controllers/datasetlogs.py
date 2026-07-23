from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.configs import auth
from app.data.database import get_session
from app.services import datasetlogs


router = APIRouter(prefix="/datasetlogs")

@router.get("/")
@auth.authenticated
def search(
    page:int = Query(1),
    size:int = Query(10),
    session:Session = Depends(get_session)):
    return datasetlogs.search(page, size, session)