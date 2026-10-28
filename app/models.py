from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class EvaluationItem(BaseModel):
    id: str = Field(min_length=1, max_length=100)
    prompt: str = Field(min_length=1, max_length=10000)
    response_a: str = Field(min_length=1, max_length=20000)
    response_b: str = Field(min_length=1, max_length=20000)
    topic: str = Field(default="general", max_length=100)


class ImportRequest(BaseModel):
    records: list[EvaluationItem] = Field(min_length=1, max_length=1000)


class Scores(BaseModel):
    correctness: int = Field(ge=1, le=5)
    instruction_adherence: int = Field(ge=1, le=5)
    completeness: int = Field(ge=1, le=5)
    evidence_quality: int = Field(ge=1, le=5)
    clarity: int = Field(ge=1, le=5)


class EvaluationCreate(BaseModel):
    item_id: str = Field(min_length=1, max_length=100)
    evaluator_id: str = Field(min_length=1, max_length=100)
    scores_a: Scores
    scores_b: Scores
    decision: Literal["A", "B", "tie", "unable_to_judge"]
    justification: str = Field(min_length=10, max_length=4000)
    safety_concern: bool = False
    insufficient_evidence: bool = False

    @field_validator("justification")
    @classmethod
    def justification_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Justification cannot be blank")
        return value.strip()


class AdjudicationUpdate(BaseModel):
    note: str = Field(min_length=1, max_length=4000)

    @field_validator("note")
    @classmethod
    def note_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Adjudication note cannot be blank")
        return value.strip()


class Rubric(BaseModel):
    version: str = "1.0"
    weights: dict[str, float] = Field(default_factory=lambda: {
        "correctness": 0.40,
        "instruction_adherence": 0.25,
        "completeness": 0.15,
        "evidence_quality": 0.10,
        "clarity": 0.10,
    })

    @field_validator("weights")
    @classmethod
    def validate_weights(cls, weights: dict[str, float]) -> dict[str, float]:
        expected = {"correctness", "instruction_adherence", "completeness", "evidence_quality", "clarity"}
        if set(weights) != expected or any(v < 0 for v in weights.values()):
            raise ValueError("Weights must contain all five rubric dimensions with non-negative values")
        if abs(sum(weights.values()) - 1.0) > 1e-8:
            raise ValueError("Rubric weights must sum to 1.0")
        return weights


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
