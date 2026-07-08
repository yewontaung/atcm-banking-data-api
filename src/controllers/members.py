from fastapi import APIRouter


router = APIRouter(prefix="/members")

@router.get("/")
def index():...

@router.get("/{member_id}")
def detail():...

@router.post("/")
def save():...

@router.patch("/")
def approve():...