from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.data.database import get_session
from app.dtos.inputs import SignInForm
from app.dtos.outputs import AuthResult
from app.services import accounts


router = APIRouter(prefix="/auth")

@router.post("/sign-in", response_model=AuthResult)
def sign_in(form:SignInForm, session:Session = Depends(get_session)):
    return accounts.sign_in(form, session)