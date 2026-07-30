from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.services.auth import get_current_user_id
from app.services.words_repository import get_cognates

router = APIRouter(prefix="/library", tags=["library"])


class CognateWord(BaseModel):
    id: int
    term: str
    translation_pt: str


@router.get("/cognates", response_model=list[CognateWord])
def cognates(user_id: int = Depends(get_current_user_id)):
    """Palavras muito parecidas com o português — não entram nas lições/exercícios,
    ficam só como referência rápida."""
    words = get_cognates()
    return [CognateWord(id=w["id"], term=w["term"], translation_pt=w["translation_pt"]) for w in words]
