from fastapi import APIRouter, Depends

from app.configs import auth
from app.controllers import dashboard, datasets, intents, me, members, ners
import app.controllers.auth


annonymous = APIRouter()
authenticated = APIRouter(dependencies=[Depends(auth.get_current_user)])

# annonymous routes
annonymous.include_router(router=app.controllers.auth.router)

# authenticated routes
authenticated.include_router(router=members.router)
authenticated.include_router(router=me.router)
authenticated.include_router(router=ners.router)
authenticated.include_router(router=intents.router)
authenticated.include_router(router=datasets.router)
authenticated.include_router(router=dashboard.router)
