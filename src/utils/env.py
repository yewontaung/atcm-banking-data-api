import os

from dotenv import load_dotenv


load_dotenv()

def get_env(name:str) -> str:
    return os.getenv(name)

DEV = "DEV"
DATABASE_URL = "DATABASE_URL"
JWT_SECRET = "JWT_SECRET"
ALGO = "ALGO"
ADMIN_EMAIL = "ADMIN_EMAIL"
ADMIN_NAME = "ADMIN_NAME"
ADMIN_PASSWORD = "ADMIN_PASSWORD"
# DATABASE_PASSWORD = "DATABASE_PASSWORD"