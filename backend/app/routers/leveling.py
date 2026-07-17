from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.demo_user import get_demo_user_id
from app.services.progress_repository import mark_known_at_onboarding
from app.services.similarity import check_translation_answer
from app.services.words_repository import get_next_untested_word, get_word_by_id

router = APIRouter(prefix="/leveling", tags=["leveling"])


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


@router.get("/next-word", response_model=WordPublic | None)
def next_word(exclude: str = Query(default="")):
    """Próxima palavra do teste adaptativo: a mais frequente que o usuário ainda não tem
    progresso registrado, pulando as já testadas nesta sessão (query param `exclude`,
    ids separados por vírgula)."""
    exclude_ids = [int(x) for x in exclude.split(",") if x]
    user_id = get_demo_user_id()
    word = get_next_untested_word(user_id, exclude_ids)
    if word is None:
        return None
    return WordPublic(id=word["id"], term=word["term"])


@router.post("/check", response_model=CheckAnswerResponse)
def check_answer(payload: CheckAnswerRequest):
    word = get_word_by_id(payload.word_id)
    if word is None:
        raise HTTPException(status_code=404, detail="Palavra não encontrada")

    result = check_translation_answer(word["translation_pt"], payload.answer)

    if result["correct"]:
        user_id = get_demo_user_id()
        mark_known_at_onboarding(user_id, payload.word_id)

    return CheckAnswerResponse(
        correct=result["correct"],
        similarity=result["similarity"],
        correct_translation=word["translation_pt"],
    )
