import csv
import io
import json
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse

from app.models import AdjudicationUpdate, EvaluationCreate, EvaluationItem, ImportRequest, Rubric
from app import storage

app = FastAPI(title="AI Response Evaluation Platform", version="0.1.0",
              description="Local-first evaluator for comparing AI responses with a versioned rubric.")
storage.initialize()
rubric = Rubric()


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/items")
def items():
    return storage.list_items()


@app.post("/api/items/import")
def import_json(payload: ImportRequest):
    storage.import_items(payload.records)
    return {"imported": len(payload.records)}


@app.post("/api/items/import-file")
async def import_file(file: UploadFile = File(...)):
    raw = await file.read(2_000_001)
    return import_file_content(file.filename or "", raw)


def import_file_content(filename: str, raw: bytes):
    name = filename.lower()
    if len(raw) > 2_000_000:
        raise HTTPException(413, "Import file exceeds 2 MB")
    try:
        text = raw.decode("utf-8-sig")
        if name.endswith(".json"):
            rows = json.loads(text)
        elif name.endswith(".csv"):
            rows = list(csv.DictReader(io.StringIO(text)))
        else:
            raise HTTPException(400, "Upload a .json or .csv file")
        records = [EvaluationItem.model_validate(row) for row in rows]
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(400, f"Could not validate import: {exc}") from exc
    if not records:
        raise HTTPException(400, "Import must contain at least one record")
    storage.import_items(records)
    return {"imported": len(records)}


@app.get("/api/rubric")
def get_rubric():
    return rubric.model_dump()


@app.put("/api/rubric")
def update_rubric(payload: Rubric):
    global rubric
    rubric = payload
    return {"updated": True, **rubric.model_dump()}


@app.post("/api/evaluations", status_code=201)
def create_evaluation(payload: EvaluationCreate):
    if not storage.get_item(payload.item_id):
        raise HTTPException(404, "Evaluation item not found")
    return storage.save_evaluation(payload, rubric)


@app.get("/api/evaluations")
def evaluations(search: str = "", decision: str = ""):
    return storage.list_evaluations(search, decision)


@app.patch("/api/evaluations/{evaluation_id}/adjudication")
def adjudicate(evaluation_id: int, payload: AdjudicationUpdate):
    if not storage.update_adjudication(evaluation_id, payload):
        raise HTTPException(404, "Evaluation not found")
    return {"updated": True, "evaluation_id": evaluation_id}


@app.get("/api/reports/disagreements")
def disagreements():
    return storage.disagreement_review()


@app.get("/api/reports/summary")
def report_summary():
    return storage.summary()


@app.get("/api/reports/export.csv")
def export_csv():
    rows = storage.export_rows()
    fields = list(rows[0].keys()) if rows else ["id", "item_id", "decision"]
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
    buffer.seek(0)
    return StreamingResponse(iter([buffer.getvalue()]), media_type="text/csv",
                             headers={"Content-Disposition": "attachment; filename=evaluations.csv"})


@app.get("/api/reports/export.json")
def export_json():
    return storage.export_rows()
