from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.configs import auth
from app.data.database import get_session
from app.services import dashboard


router = APIRouter(prefix="/dashboard")

@router.get("/")
@auth.authenticated
def analysis(session:Session = Depends(get_session)):
    return dashboard.analysis(session)