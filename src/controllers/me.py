from fastapi import APIRouter, Depends
from sqlmodel import Session

from configs import auth
from data import database
from services import accounts
from utils.managers.security import SecurityContext


router = APIRouter(prefix="/me")

@router.get("/profile")
@auth.authenticated
def profile(session:Session = Depends(database.get_session)):
    return accounts.profile(SecurityContext.get_user().userid, session)