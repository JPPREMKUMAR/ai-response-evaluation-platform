from app import main
from app.models import AdjudicationUpdate, EvaluationCreate, ImportRequest

SCORES = {"correctness":5,"instruction_adherence":5,"completeness":5,"evidence_quality":4,"clarity":5}

def test_import_evaluate_and_summary():
    response = main.import_json(ImportRequest(records=[{"id":"t1","prompt":"Answer simply","response_a":"A","response_b":"B","topic":"demo"}]))
    assert response == {"imported": 1}
    created = main.create_evaluation(EvaluationCreate(item_id="t1",evaluator_id="reviewer-1",scores_a=SCORES,scores_b={**SCORES,"correctness":2},decision="A",justification="A follows the prompt and is better supported."))
    assert created["score_a"] > created["score_b"]
    assert main.report_summary()["evaluation_count"] == 1

def test_evaluation_requires_known_item():
    from fastapi import HTTPException
    import pytest
    payload = EvaluationCreate(item_id="missing",evaluator_id="r",scores_a=SCORES,scores_b=SCORES,decision="tie",justification="Both answers are equivalent in this case.")
    with pytest.raises(HTTPException) as error:
        main.create_evaluation(payload)
    assert error.value.status_code == 404

def test_csv_export_has_content_type_when_empty():
    response = main.export_csv()
    assert response.media_type == "text/csv"
    assert "evaluations.csv" in response.headers["content-disposition"]

def test_rubric_can_be_updated_and_is_recorded():
    from app.models import Rubric
    updated = main.update_rubric(Rubric(version="1.1", weights={"correctness":0.5,"instruction_adherence":0.2,"completeness":0.1,"evidence_quality":0.1,"clarity":0.1}))
    assert updated["version"] == "1.1"
    main.import_json(ImportRequest(records=[{"id":"t2","prompt":"p","response_a":"a","response_b":"b"}]))
    result = main.create_evaluation(EvaluationCreate(item_id="t2",evaluator_id="r",scores_a=SCORES,scores_b=SCORES,decision="tie",justification="Both responses satisfy the stated requirements."))
    assert result["rubric_version"] == "1.1"

def test_disagreement_review_and_adjudication_note():
    main.import_json(ImportRequest(records=[{"id":"t3","prompt":"p","response_a":"a","response_b":"b"}]))
    first = main.create_evaluation(EvaluationCreate(item_id="t3",evaluator_id="r1",scores_a=SCORES,scores_b=SCORES,decision="A",justification="A is clearer and preserves the requested detail."))
    second = main.create_evaluation(EvaluationCreate(item_id="t3",evaluator_id="r2",scores_a=SCORES,scores_b=SCORES,decision="B",justification="B gives a more direct response to the prompt."))
    assert main.disagreements()[0]["item_id"] == "t3"
    assert main.adjudicate(first["id"], AdjudicationUpdate(note="Adjudicator selected A because it covers the explicit condition."))["updated"]
    assert any(row["adjudication_note"] for row in main.evaluations())

def test_csv_file_import():
    result = main.import_file_content("rows.csv", b"id,prompt,response_a,response_b,topic\ncsv-1,Question,A,B,topic")
    assert result["imported"] == 1
    assert main.items()[0]["id"] == "csv-1"
