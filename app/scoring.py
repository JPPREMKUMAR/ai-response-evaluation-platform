from app.models import Rubric, Scores


def weighted_score(scores: Scores, rubric: Rubric) -> float:
    return round(sum(getattr(scores, key) * weight for key, weight in rubric.weights.items()), 3)
