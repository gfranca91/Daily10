LEVEL_ORDER = ["A1", "A2", "B1", "B2", "C1", "C2"]

# Faixas de frequency_rank -> nível CEFR (aproximação por frequência, não é
# uma classificação linguística oficial). Ajustar conforme o vocabulário cresce.
LEVEL_BANDS = [
    (1, 120, "A1"),
    (121, 260, "A2"),
    (261, 420, "B1"),
    (421, 600, "B2"),
    (601, 800, "C1"),
    (801, 10_000, "C2"),
]


def level_for_rank(frequency_rank: int) -> str:
    for low, high, level in LEVEL_BANDS:
        if low <= frequency_rank <= high:
            return level
    return LEVEL_ORDER[-1]
