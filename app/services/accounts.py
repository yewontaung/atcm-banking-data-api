from pathlib import Path

from fastapi import UploadFile
import jwt
from sqlmodel import Session, func, select

from app.data.database import safe_call
from app.data.enums import DatasetType
from app.data.models import Account, Dataset
from app.dtos.inputs import PasswordForm, SignInForm
from app.dtos.outputs import AuthProfile, AuthResult, ModificationResult, Profile, ProfileUploadResult
from app.utils import env, upload
from app.utils.exceptions import AppBusinessException
from app.utils.singletons import hash_password, verify_password


def sign_in(form:SignInForm, session:Session) -> AuthResult:
    account = safe_call(session.exec(select(Account).where(Account.account_email == form.account_email)).one_or_none(), "Account", "account_email", form.account_email)
    if not verify_password(form.password, account.hashed_password):
        raise AppBusinessException("Wrong password.")
    payload = {
        "account_id": account.account_id,
        "account_email": account.account_email,
        "account_role": account.role.name,
    }
    access_token = jwt.encode(payload=payload, key=env.JWT_SECRET, algorithm=env.ALGO)
    return AuthResult(
        profile=AuthProfile(
            account_id=account.account_id,
            account_name=account.name,
            account_email=account.account_email,
            account_role=account.role,
            profile_url=account.profile_url,
        ),
        access_token=access_token,
    )

def profile(user_id:str, session:Session) -> Profile:
    account = safe_call(session.get(Account, user_id), "Account", "account_id", user_id)
    DATASET_COUNT = (select(
        Dataset.dataset_type,
        func.count(Dataset.dataset_id)
    ).select_from(Dataset)
    .where(Dataset.member_id == account.account_id, Dataset.deleted == False)
    .group_by(Dataset.dataset_type))

    training_dataset = 0
    validation_dataset = 0
    testing_dataset = 0

    result = session.exec(DATASET_COUNT).all()

    for dataset_type, count in result:
        match dataset_type:
            case DatasetType.Training: training_dataset += count
            case DatasetType.Validation: validation_dataset += count
            case DatasetType.Testing: validation_dataset += count


    return Profile(
        account_id=account.account_id,
        account_name=account.name,
        account_email=account.account_email,
        account_role=account.role,
        profile_url=account.profile_url,
        training_dataset=training_dataset,
        validation_dataset=validation_dataset,
        testing_dataset=testing_dataset,
    )

def change_password(form:PasswordForm, user_id:str, session:Session) -> ModificationResult[int]:
    account = safe_call(session.get(Account, user_id), "Account", "user_id", user_id)
    if not verify_password(form.old_password, account.hashed_password):
        raise AppBusinessException("Wrong password.")
    if form.old_password == form.new_password:
        raise AppBusinessException("New password cannot be old password.")
    if not form.is_valid:
        raise AppBusinessException("New password and confirm password are not same.")

    account.hashed_password = hash_password(form.new_password)
    session.add(account)
    session.commit()
    return ModificationResult(result_data=account.account_id)

async def upload_profile_image(file:UploadFile, user_id:str, session:Session) -> ProfileUploadResult:
    account = safe_call(session.get(Account, user_id), "Account", "user_id", user_id)
    extension  = Path(file.filename).suffix
    if extension != ".jpg" and extension != ".jpeg" and extension != ".png":
        raise AppBusinessException(f"App doesn't support {extension} files.")
    
    filename = f"{account.account_id}-{account.account_email.split("@")[0]}{extension}"

    # profile_image_dir = Path(env.PROFILE_IMAGE_DIR)
    # profile_image_dir.mkdir(parents=True, exist_ok=True)

    # filepath = profile_image_dir / filename

    # with filepath.open("wb") as buffer:
    #     buffer.write(file.file.read())
    
    # account.profile_url = f"/{env.PROFILE_IMAGE_DIR}/{filename}"

    image = await file.read()
    url = upload.upload(filename=filename, content=image, content_type=file.content_type)
    account.profile_url = url

    session.add(account)
    session.commit()
    session.refresh(account)

    return ProfileUploadResult(image_url=account.profile_url)
