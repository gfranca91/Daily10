from datetime import date, timedelta

MIN_EASINESS_FACTOR = 1.3


def apply_sm2(repetitions: int, easiness_factor: float, interval_days: int, correct: bool, today: date | None = None) -> dict:
    """Algoritmo SM-2. Nossa UI é binária (certo/errado) em vez de uma nota de 0 a 5,
    então mapeamos: acertou -> quality 5, errou -> quality 2 (abaixo do limiar 3, reseta)."""
    today = today or date.today()
    quality = 5 if correct else 2

    new_easiness_factor = easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    new_easiness_factor = max(MIN_EASINESS_FACTOR, new_easiness_factor)

    if quality < 3:
        new_repetitions = 0
        new_interval_days = 1
    else:
        new_repetitions = repetitions + 1
        if new_repetitions == 1:
            new_interval_days = 1
        elif new_repetitions == 2:
            new_interval_days = 6
        else:
            new_interval_days = round(interval_days * new_easiness_factor)

    return {
        "repetitions": new_repetitions,
        "easiness_factor": round(new_easiness_factor, 2),
        "interval_days": new_interval_days,
        "due_date": today + timedelta(days=new_interval_days),
    }
