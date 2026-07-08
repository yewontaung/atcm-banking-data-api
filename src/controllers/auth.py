from fastapi import APIRouter


router = APIRouter(prefix="/auth")

@router.post("/sign-in")
def sign_in():...