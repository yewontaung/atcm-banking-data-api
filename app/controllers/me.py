from fastapi import APIRouter, Depends, UploadFile
from sqlmodel import Session

from app.configs import auth
from app.data import database
from app.dtos.inputs import PasswordForm
from app.services import accounts
from app.utils.managers.security import SecurityContext


router = APIRouter(prefix="/me")

@router.get("/profile")
@auth.authenticated
def profile(session:Session = Depends(database.get_session)):
    return accounts.profile(SecurityContext.get_user().user_id, session)

@router.post("/profile/upload")
@auth.authenticated
async def upload(file:UploadFile, session:Session = Depends(database.get_session)):
    return await accounts.upload_profile_image(file, SecurityContext.get_user().user_id, session)

@router.post("/change-password")
@auth.authenticated
def password(form:PasswordForm, session:Session = Depends(database.get_session)):
    return accounts.change_password(form, SecurityContext.get_user().user_id, session)