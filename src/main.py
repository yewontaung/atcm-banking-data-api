from fastapi import FastAPI

from app import routes


app = FastAPI()

app.include_router(router=routes.annonymous)
app.include_router(router=routes.authenticated)

if __name__ == "__main__":
    print("app is running.")