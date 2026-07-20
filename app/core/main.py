from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core import handlers, routes
from app.data import database
from app.utils import env
from app.utils.exceptions import AppBusinessException, ResourceNotFoundException
from app.utils.managers.security import SecurityException

@asynccontextmanager
async def lifespan(app:FastAPI):

    # database.create_tables()

    database.seed_admin()

    print("==============================")
    print("ATCM API is started.")
    print("==============================")
    
    yield

    print("==============================")
    print("ATCM API is ended.")
    print("==============================")

app = FastAPI(lifespan=lifespan)

app.exception_handler(ResourceNotFoundException)(handlers.handle_resource_notfound_exception)
app.exception_handler(AppBusinessException)(handlers.handle_app_business_exception)
app.exception_handler(SecurityException)(handlers.handle_security_exception)

app.include_router(router=routes.annonymous)
app.include_router(router=routes.authenticated)

origins = env.ALLOWED_ORIGINS.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# if __name__ == "__main__":
#     uvicorn.run(app="main:app", reload=True)