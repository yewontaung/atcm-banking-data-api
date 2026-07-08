from fastapi import APIRouter


router = APIRouter(prefix="/ners")

@router.get("/")
def index():...

@router.get("/{ner_id}")
def detail():...

@router.post("/")
def save():...