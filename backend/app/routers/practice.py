import random

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.services.auth import get_current_user_id
from app.services.practice_repository import check_practice_answer, get_practice_exercises_for_words
from app.services.progress_repository import get_review_due_word_ids, get_today_lesson_word_ids

router = APIRouter(prefix="/practice", tags=["practice"])


class OptionPublic(BaseModel):
    word_id: int
    term: str


class ExercisePublic(BaseModel):
    sentence_id: int
    sentence_template: str
    options: list[OptionPublic]


class CheckPracticeRequest(BaseModel):
    sentence_id: int
    option_word_id: int


class CheckPracticeResponse(BaseModel):
    correct: bool
    correct_term: str


def _build_exercises(word_ids: list[int]) -> list[ExercisePublic]:
    exercises = get_practice_exercises_for_words(word_ids)
    result = []
    for ex in exercises:
        options = ex["options"][:]
        random.shuffle(options)
        result.append(ExercisePublic(sentence_id=ex["sentence_id"], sentence_template=ex["sentence_template"], options=options))
    return result


@router.get("/review", response_model=list[ExercisePublic])
def review_practice(user_id: int = Depends(get_current_user_id)):
    """Revisão das palavras de dias anteriores que o SM-2 agendou pra hoje.
    Vem ANTES da lição do dia no fluxo (revisão > lição nova > exercícios da lição)."""
    word_ids = get_review_due_word_ids(user_id)
    return _build_exercises(word_ids)


@router.get("/today", response_model=list[ExercisePublic])
def today_practice(user_id: int = Depends(get_current_user_id)):
    """Exercícios de fixação só das palavras novas aprendidas na lição de HOJE."""
    word_ids = get_today_lesson_word_ids(user_id)
    return _build_exercises(word_ids)


@router.post("/check", response_model=CheckPracticeResponse)
def check_practice(payload: CheckPracticeRequest, user_id: int = Depends(get_current_user_id)):
    result = check_practice_answer(user_id, payload.sentence_id, payload.option_word_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Exercício não encontrado")
    return CheckPracticeResponse(correct=result["is_correct"], correct_term=result["correct_term"])
