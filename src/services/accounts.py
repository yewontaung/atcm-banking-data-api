import jwt
from sqlmodel import Session, select

from data.database import safe_call
from data.models import Account
from dtos.inputs import SignInForm
from dtos.outputs import AuthResult
from utils import env
from utils.exceptions import AppBusinessException
from utils.singletons import verify_password


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
        account_id=account.account_id,
        account_name=account.name,
        account_email=account.account_email,
        account_role=account.role,
        profile_url=account.profile_url,
        access_token=access_token,
    )