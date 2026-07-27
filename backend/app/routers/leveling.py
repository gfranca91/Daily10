from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.services.auth import complete_placement, get_current_user_id
from app.services.progress_repository import mark_known_at_onboarding
from app.services.similarity import check_translation_answer
from app.services.words_repository import get_next_word_at_level, get_word_by_id

router = APIRouter(prefix="/leveling", tags=["leveling"])

CefrLevel = Literal["A1", "A2", "B1", "B2", "C1", "C2"]


class WordPublic(BaseModel):
    id: int
    term: str


class CheckAnswerRequest(BaseModel):
    word_id: int
    answer: str


class CheckAnswerResponse(BaseModel):
    correct: bool
    similarity: float
    correct_translation: str


class CompletePlacementRequest(BaseModel):
    confirmed_level: CefrLevel


@router.get("/next-word", response_model=WordPublic | None)
def next_word(level: CefrLevel = Query(), exclude: str = Query(default=""), user_id: int = Depends(get_current_user_id)):
    """Próxima palavra do teste de nivelamento adaptativo DENTRO de um nível CEFR
    (o frontend decide qual nível testar e quando subir/descer de nível)."""
    exclude_ids = [int(x) for x in exclude.split(",") if x]
    word = get_next_word_at_level(level, exclude_ids)
    if word is None:
        return None
    return WordPublic(id=word["id"], term=word["term"])


@router.post("/check", response_model=CheckAnswerResponse)
def check_answer(payload: CheckAnswerRequest, user_id: int = Depends(get_current_user_id)):
    word = get_word_by_id(payload.word_id)
    if word is None:
        raise HTTPException(status_code=404, detail="Palavra não encontrada")

    result = check_translation_answer(word["translation_pt"], payload.answer)

    if result["correct"]:
        mark_known_at_onboarding(user_id, payload.word_id)

    return CheckAnswerResponse(
        correct=result["correct"],
        similarity=result["similarity"],
        correct_translation=word["translation_pt"],
    )


@router.post("/complete-placement")
def finish_placement(payload: CompletePlacementRequest, user_id: int = Depends(get_current_user_id)):
    complete_placement(user_id, payload.confirmed_level)
    return {"status": "ok"}
