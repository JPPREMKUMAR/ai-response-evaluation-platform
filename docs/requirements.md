# Product requirements and acceptance criteria

## Problem and users

Reviewers need a consistent way to compare two answers to the same prompt, explain a preference, flag safety or evidence concerns, and inspect agreement without treating a synthetic sample as model-performance evidence. Primary users are individual evaluators and small research-quality teams.

## MVP behavior

1. Import JSON or CSV records and reject invalid records with actionable validation errors.
2. Show response A and B for one prompt and require five 1–5 rubric scores, a preference, and a written rationale.
3. Store pseudonymous evaluator ID, timestamp, rubric version, scores, safety concern, and insufficient-evidence flags.
4. Search/filter stored records, surface conflicting evaluator choices, and attach an adjudication note.
5. Export JSON/CSV and report counts, sample sizes, and missingness.

## Acceptance checks

- Weighted scores use the versioned rubric and sum to the configured weight total.
- Missing rationale, out-of-range scores, malformed imports, and duplicate IDs are rejected.
- A/B/tie/unable decisions and independent flags persist and can be exported.
- Empty datasets and unresolved disagreements are represented without fabricated values.
- Unit and API workflow tests plus a production frontend build pass.

## Risks and limits

The current build is a local-first prototype with no authentication, role permissions, pagination, or durable remote database. The active rubric configuration is in process memory and resets on restart; saved evaluations retain their rubric version. Never use it for confidential review data until access control, retention, and deployment storage are addressed.
