from fastapi import APIRouter, Depends
from sqlmodel import Session

from data.database import get_session
from dtos.inputs import SignInForm
from services import accounts


router = APIRouter(prefix="/auth")

@router.post("/sign-in")
def sign_in(form:SignInForm, session:Session = Depends(get_session)):
    return accounts.sign_in(form, session)