# Test report — 2026-10-28

Environment: Windows host, Python 3.12.14 bundled runtime, pytest 8.3.5, Node.js 22, npm 10.9.x, Vite 6.4.5.

| Check | Result | Evidence |
|---|---|---|
| Backend unit and workflow tests | **Passed: 9, failed: 0, skipped: 0** | `python -m pytest -q` |
| Frontend TypeScript and production build | **Passed** | `npm run build` in `frontend/`; 28 modules transformed |
| API health smoke check | **Passed** | `GET /api/health` returned `ok` |
| API import → evaluate → summary smoke workflow | **Passed** | Imported 1 record; saved evaluation; summary count 1; scores A 4.9 and B 2.7 |
| Disagreement and adjudication smoke check | **Passed** | Two conflicting synthetic ratings produced one disagreement; adjudication note saved |
| CSV export | **Passed** | Live endpoint returned HTTP 200 with CSV attachment header; automated test checks empty export behavior |
| Manual browser workflow | **Passed at the current browser viewport** | Loaded the three synthetic items, reviewed the ambiguous example, submitted an `unable_to_judge` decision with rationale, and saw the saved evaluation in review history |
| Lint/type check | **No separate lint configured; TypeScript type check passed** | `tsc -b` ran as part of the frontend build; no Python static type checker is configured |
| Deployment | **Not deployed** | No remote service configured for this API and its persistent SQLite data |
| GitHub publication | **Published** | Public GitHub snapshot on `main`; source files verified |

The API smoke test used synthetic data and verifies application behavior only. It is not evidence about any real model. An initial test run exposed SQLite connections left open; the connection lifecycle was corrected and the final test run passed. An initial frontend build found an unsupported string method for the configured TypeScript target; it was corrected before the passing build.

Known gaps: no HTTP integration test framework result is claimed (the local TestClient stalled in this Windows environment); the smoke tests used a running local Uvicorn server instead. No deployed smoke test, independent evaluator agreement, security penetration test, or systematic desktop/mobile breakpoint matrix has been performed.

