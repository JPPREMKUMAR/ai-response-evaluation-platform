# Response-quality examples

These hand-authored examples exercise the comparison rubric. They are synthetic and are not model benchmark results.

| Case | Prompt and candidate answer | Objective evaluation |
|---|---|---|
| Correct | “What is 2 + 2?” A: “4.” B: “5.” | Prefer A for correctness; state the arithmetic as evidence. |
| Incorrect | “At standard pressure, what is water’s freezing point in °C?” A: “0 °C.” B: “50 °C.” | Prefer A; B is factually incorrect under the stated condition. |
| Incomplete | “Give three examples of renewable energy.” A lists solar, wind, and hydro. B says only “solar.” | Prefer A for completeness; B omits two requested examples. |
| Misleading | “Are all bacteria harmful?” A: “No; many are harmless or beneficial.” B: “Yes, every bacterium causes disease.” | Prefer A; B's absolute wording overgeneralizes. |
| Ambiguous | “Which response is better?” with no candidate responses or criteria. | Choose unable-to-judge; request the missing candidates and criteria instead of guessing. |
| Poorly formatted | “Return valid JSON with answer and confidence.” B: `{"answer":"4","confidence":}` | Flag the malformed structure under instruction adherence/clarity; do not parse a partial answer as valid JSON. |

For a fair comparison, use the same rubric version and score each dimension independently before selecting A/B/tie/unable. Record evidence in the rationale and mark insufficient evidence separately from correctness.
