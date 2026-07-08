from fastapi import APIRouter


router = APIRouter(prefix="/intents")

@router.get("/")
def index():...

@router.get("/{intent_id}")
def detail():...

@router.post("/")
def save():...

@router.patch("/")
def approve():...