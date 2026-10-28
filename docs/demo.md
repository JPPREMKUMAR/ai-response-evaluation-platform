# Demonstration script

1. Start the API and frontend using the README's local run instructions.
2. Open the review interface and import `data/examples.json`.
3. Open `date-001`; compare both answers to the exact prompt. Rate each response on all five dimensions, choose A, and enter a short evidence-based justification.
4. Mark whether insufficient evidence or a safety concern applies; do not infer either from the preference alone.
5. Open the summary, disagreement report, and CSV export.

**Expected behavior:** Import creates three items. The date example favors the January 1 answer; the password example shows a format/instruction issue in B; the last example is underdetermined and should invite an unable-to-judge decision. Counts describe only the local sample.
