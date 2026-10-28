# Evaluation methodology

## Decision process

1. Read the prompt and note its explicit constraints.
2. Score each response independently on correctness, instruction adherence, completeness, evidence quality, and clarity (1–5).
3. Select A, B, tie, or unable to judge. The weighted total is descriptive and does not override evidence or task-specific priorities.
4. Record a written justification that names the criterion and the evidence in the response.
5. Mark safety concerns and insufficient evidence as separate flags.

## Rubric v1.0

| Dimension | Weight | 1 | 3 | 5 |
|---|---:|---|---|---|
| Correctness | 40% | Materially wrong | Partly correct or contains an important error | Correct on the key claims |
| Instruction adherence | 25% | Misses central constraints | Meets some constraints | Meets all explicit constraints |
| Completeness | 15% | Omits essential parts | Covers most requested parts | Covers all requested parts at suitable depth |
| Evidence quality | 10% | Unsupported or misleading | Some support, with gaps | Claims are appropriately supported or qualified |
| Clarity | 10% | Hard to understand | Understandable with some friction | Clear and well organized |

Intermediate scores 2 and 4 represent performance between the anchors. Use “unable to judge” when the prompt or available evidence does not support a defensible comparison. Do not turn uncertainty into a false verdict.

## Metrics

Weighted score is the sum of each 1–5 dimension multiplied by its rubric weight. Decision counts and flagged counts are descriptive of the records stored here. They are not estimates of overall model quality. This MVP does not yet calculate inter-rater agreement because it has no independent second-review workflow.

## Synthetic examples

`data/examples.json` covers a stable date fact, a formatting and caution constraint, and an underspecified comparison request. Labels and example content are fictional task data; they are not a real model benchmark.
