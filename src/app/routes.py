from fastapi import APIRouter, Depends

from configs import auth
from controllers import members
import controllers.auth


annonymous = APIRouter()
authenticated = APIRouter(dependencies=[Depends(auth.get_current_user)])

# annonymous routes
annonymous.include_router(router=controllers.auth.router)

# authenticated routes
authenticated.include_router(router=members.router)