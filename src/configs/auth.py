from http import HTTPStatus

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlmodel import Session

from data.database import get_session, safe_call
from data.models import Account
from utils import env
from utils.exceptions import ResourceNotFoundException
from utils.managers.security import SecurityContext, DefaultSecurityManager, SecurityUser


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

async def get_current_user(token:str = Depends(oauth2_scheme), session:Session = Depends(get_session)):
    try:
        payload = jwt.decode(jwt=token, key=env.JWT_SECRET, algorithms=env.ALGO)
        account_id = payload.get("account_id", None)
        account = safe_call(session.get(Account, account_id), "Account", "account_id", account_id)
        user = SecurityUser(
            user_id=account.account_id,
            username=account.account_email,
            roles=frozenset({account.role.name}),
        )
        print(user.roles)
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid token.")
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=e.message)
    except Exception as e:
        print("========error========")
        print(e)
        print("========error========")
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Authorization fails.")
    
    user_token = SecurityContext.set_user(user=user)
    try:
        yield user
    finally:
        SecurityContext.reset_user(user_token)


sec = DefaultSecurityManager()

has_roles = sec.has_roles
authenticated = sec.authenticated