from fastapi import APIRouter, Depends

from configs import auth
from controllers import intents, me, members, ners
import controllers.auth


annonymous = APIRouter()
authenticated = APIRouter(dependencies=[Depends(auth.get_current_user)])

# annonymous routes
annonymous.include_router(router=controllers.auth.router)

# authenticated routes
authenticated.include_router(router=members.router)
authenticated.include_router(router=me.router)
authenticated.include_router(router=ners.router)
authenticated.include_router(router=intents.router)
