import os

from dotenv import load_dotenv


load_dotenv()

def get_env(name:str) -> str:
    return os.getenv(name)

DEV = "DEV"
DATABASE_URL = "DATABASE_URL"
# DATABASE_PASSWORD = "DATABASE_PASSWORD"