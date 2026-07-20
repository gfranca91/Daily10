from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.services.auth import get_current_user_id
from app.services.progress_repository import assign_daily_lesson, get_today_lesson_word_ids
from app.services.words_repository import get_unseen_words, get_words_by_ids

router = APIRouter(prefix="/lessons", tags=["lessons"])

WORDS_PER_LESSON = 10


class LessonWord(BaseModel):
    id: int
    term: str
    translation_pt: str
    example_sentence: str


@router.get("/today", response_model=list[LessonWord])
def today_lesson(user_id: int = Depends(get_current_user_id)):
    """Lição de hoje: até 10 palavras novas (nunca vistas), com tradução e frase de contexto.
    Idempotente — recarregar no mesmo dia devolve as mesmas palavras."""
    today_ids = get_today_lesson_word_ids(user_id)
    if not today_ids:
        new_words = get_unseen_words(user_id, WORDS_PER_LESSON)
        assign_daily_lesson(user_id, [w["id"] for w in new_words])
        words = new_words
    else:
        words = get_words_by_ids(today_ids)

    return [
        LessonWord(
            id=w["id"],
            term=w["term"],
            translation_pt=w["translation_pt"],
            example_sentence=w["example_sentence"],
        )
        for w in words
    ]
