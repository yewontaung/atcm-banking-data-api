import os

from dotenv import load_dotenv


load_dotenv()

def get_env(name:str) -> str:
    return os.getenv(name)

DEV = get_env("DEV")
DATABASE_URL = get_env("DATABASE_URL")
JWT_SECRET = get_env("JWT_SECRET")
ALGO = get_env("ALGO")
ADMIN_EMAIL = get_env("ADMIN_EMAIL")
ADMIN_NAME = get_env("ADMIN_NAME")
ADMIN_PASSWORD = get_env("ADMIN_PASSWORD")
DEFAULT_PASSWORD = get_env("DEFAULT_PASSWORD")
# DATABASE_PASSWORD = "DATABASE_PASSWORD"