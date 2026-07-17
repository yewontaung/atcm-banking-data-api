from fastapi import APIRouter, Depends
from sqlmodel import Session

from configs import auth
from data.database import get_session
from services import dashboard


router = APIRouter(prefix="/dashboard")

@router.get("/")
@auth.authenticated
def analysis(session:Session = Depends(get_session)):
    return dashboard.analysis(session)