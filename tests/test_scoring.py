import pytest
from pydantic import ValidationError
from app.models import Rubric, Scores, EvaluationCreate
from app.scoring import weighted_score

def test_weighted_score_uses_configured_weights():
    scores = Scores(correctness=5, instruction_adherence=4, completeness=3, evidence_quality=2, clarity=1)
    assert weighted_score(scores, Rubric()) == 3.75

def test_rubric_must_sum_to_one():
    with pytest.raises(ValidationError):
        Rubric(weights={"correctness": 1, "instruction_adherence": 0, "completeness": 0, "evidence_quality": 0, "clarity": 0.1})

def test_blank_justification_rejected():
    with pytest.raises(ValidationError):
        EvaluationCreate(item_id="x", evaluator_id="r1", scores_a={"correctness":3,"instruction_adherence":3,"completeness":3,"evidence_quality":3,"clarity":3}, scores_b={"correctness":3,"instruction_adherence":3,"completeness":3,"evidence_quality":3,"clarity":3}, decision="tie", justification="          ")
