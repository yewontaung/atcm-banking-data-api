from fastapi import APIRouter, Depends, UploadFile
from sqlmodel import Session

from configs import auth
from data import database
from dtos.inputs import PasswordForm
from services import accounts
from utils.managers.security import SecurityContext


router = APIRouter(prefix="/me")

@router.get("/profile")
@auth.authenticated
def profile(session:Session = Depends(database.get_session)):
    return accounts.profile(SecurityContext.get_user().user_id, session)

@router.post("/profile/upload")
@auth.authenticated
def upload(file:UploadFile, session:Session = Depends(database.get_session)):
    return accounts.upload_profile_image(file, SecurityContext.get_user().user_id, session)

@router.post("/change-password")
@auth.authenticated
def password(form:PasswordForm, session:Session = Depends(database.get_session)):
    return accounts.change_password(form, SecurityContext.get_user().user_id, session)