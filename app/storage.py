import json
import os
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from dotenv import load_dotenv

from app.models import AdjudicationUpdate, EvaluationCreate, EvaluationItem, Rubric, utc_now
from app.scoring import weighted_score

load_dotenv()
DB_PATH = Path(os.getenv("DATABASE_PATH", "./evaluation.db"))


def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def database():
    conn = connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def initialize():
    with database() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS items (
          id TEXT PRIMARY KEY, prompt TEXT NOT NULL, response_a TEXT NOT NULL,
          response_b TEXT NOT NULL, topic TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS evaluations (
          id INTEGER PRIMARY KEY AUTOINCREMENT, item_id TEXT NOT NULL REFERENCES items(id),
          evaluator_id TEXT NOT NULL, scores_a TEXT NOT NULL, scores_b TEXT NOT NULL,
          score_a REAL NOT NULL, score_b REAL NOT NULL, decision TEXT NOT NULL,
          justification TEXT NOT NULL, safety_concern INTEGER NOT NULL,
          insufficient_evidence INTEGER NOT NULL, rubric_version TEXT NOT NULL,
          created_at TEXT NOT NULL, adjudication_note TEXT NOT NULL DEFAULT ''
        );
        CREATE INDEX IF NOT EXISTS idx_evaluations_item ON evaluations(item_id);
        """)
        columns = {row[1] for row in db.execute("PRAGMA table_info(evaluations)")}
        if "adjudication_note" not in columns:
            db.execute("ALTER TABLE evaluations ADD COLUMN adjudication_note TEXT NOT NULL DEFAULT ''")


def list_items():
    with database() as db:
        return [dict(row) for row in db.execute("SELECT * FROM items ORDER BY id")]


def get_item(item_id: str):
    with database() as db:
        row = db.execute("SELECT * FROM items WHERE id=?", (item_id,)).fetchone()
        return dict(row) if row else None


def import_items(items: list[EvaluationItem]):
    with database() as db:
        for item in items:
            db.execute("""INSERT INTO items(id,prompt,response_a,response_b,topic)
              VALUES(?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET prompt=excluded.prompt,
              response_a=excluded.response_a,response_b=excluded.response_b,topic=excluded.topic""",
              (item.id, item.prompt, item.response_a, item.response_b, item.topic))


def save_evaluation(payload: EvaluationCreate, rubric: Rubric):
    score_a = weighted_score(payload.scores_a, rubric)
    score_b = weighted_score(payload.scores_b, rubric)
    with database() as db:
        cur = db.execute("""INSERT INTO evaluations
          (item_id,evaluator_id,scores_a,scores_b,score_a,score_b,decision,justification,
           safety_concern,insufficient_evidence,rubric_version,created_at)
          VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
          (payload.item_id, payload.evaluator_id, payload.scores_a.model_dump_json(),
           payload.scores_b.model_dump_json(), score_a, score_b, payload.decision,
           payload.justification, int(payload.safety_concern), int(payload.insufficient_evidence),
           rubric.version, utc_now()))
        return {"id": cur.lastrowid, "score_a": score_a, "score_b": score_b,
                "rubric_version": rubric.version}


def list_evaluations(search: str = "", decision: str = ""):
    query = """SELECT e.*, i.topic, i.prompt FROM evaluations e JOIN items i ON i.id=e.item_id
               WHERE (i.prompt LIKE ? OR e.justification LIKE ? OR e.item_id LIKE ?)"""
    args: list[object] = [f"%{search}%"] * 3
    if decision:
        query += " AND e.decision=?"
        args.append(decision)
    query += " ORDER BY e.created_at DESC"
    with database() as db:
        return [dict(row) for row in db.execute(query, args)]


def summary():
    with database() as db:
        total = db.execute("SELECT COUNT(*) FROM evaluations").fetchone()[0]
        decisions = {row[0]: row[1] for row in db.execute(
            "SELECT decision,COUNT(*) FROM evaluations GROUP BY decision")}
        flagged = db.execute("SELECT COUNT(*) FROM evaluations WHERE safety_concern=1 OR insufficient_evidence=1").fetchone()[0]
        return {"evaluation_count": total, "sample_size": total, "missing_data_rate": 0.0 if total else None,
                "decision_counts": decisions, "flagged_count": flagged,
                "limitations": "Metrics describe this dataset only; required fields are validated before storage, and synthetic examples do not establish real-model quality."}


def export_rows():
    return list_evaluations()


def update_adjudication(evaluation_id: int, payload: AdjudicationUpdate):
    with database() as db:
        cursor = db.execute("UPDATE evaluations SET adjudication_note=? WHERE id=?", (payload.note, evaluation_id))
        if cursor.rowcount == 0:
            return False
    return True


def disagreement_review():
    rows = list_evaluations()
    grouped: dict[str, list[dict]] = {}
    for row in rows:
        grouped.setdefault(row["item_id"], []).append(row)
    return [{"item_id": item_id, "evaluation_count": len(group),
             "decisions": sorted({row["decision"] for row in group}), "evaluations": group}
            for item_id, group in grouped.items()
            if len({row["decision"] for row in group}) > 1]
