import random

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.services.auth import get_current_user_id
from app.services.practice_repository import check_practice_answer, get_practice_exercises_for_words
from app.services.progress_repository import get_due_word_ids, record_review

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


@router.get("/today", response_model=list[ExercisePublic])
def today_practice(user_id: int = Depends(get_current_user_id)):
    """Exercícios de fixação/revisão (frase + múltipla escolha) pras palavras devidas hoje —
    tanto as novas da lição de hoje quanto as agendadas pelo SM-2. Palavras sem frase
    cadastrada ainda são simplesmente puladas."""
    word_ids = get_due_word_ids(user_id)
    exercises = get_practice_exercises_for_words(word_ids)

    result = []
    for ex in exercises:
        options = ex["options"][:]
        random.shuffle(options)
        result.append(ExercisePublic(sentence_id=ex["sentence_id"], sentence_template=ex["sentence_template"], options=options))
    return result


@router.post("/check", response_model=CheckPracticeResponse)
def check_practice(payload: CheckPracticeRequest, user_id: int = Depends(get_current_user_id)):
    result = check_practice_answer(payload.sentence_id, payload.option_word_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Exercício não encontrado")

    record_review(user_id, result["word_id"], result["is_correct"])

    return CheckPracticeResponse(correct=result["is_correct"], correct_term=result["correct_term"])
