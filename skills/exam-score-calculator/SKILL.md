---
name: "exam-score-calculator"
description: "Calculate, sort, and table exam scores for 8 subjects across 4 terms with running averages and target scores."
---

# Exam Score Calculator

Use when user provides exam scores and wants calculations, rankings, tables, running averages, or target score projections.

## Overview

The school year has **4 terms**. User is currently in **Term 2**, meaning:
- Terms 1, 2 have actual scores
- Terms 3, 4 are upcoming

## Supported Subjects

- Biology
- Chemistry
- Physics
- Mathematics
- Additional Mathematics
- Chinese
- English
- Geography

## Input Format

Accept scores in any format:

1. **Single:** "Biology Term 1: 85/100"
2. **Bulk:** "Term 1: Bio 80, Chem 75, Physics 88..."
3. **Multiple terms at once:** "Term 1: Bio 80, Chem 75 | Term 2: Bio 85, Chem 82..."

## Storage

Keep a running record in `exam-scores.json` in the workspace so the user doesn't have to re-enter previous terms every time. Structure:

```json
{
  "subjects": ["Biology", "Chemistry", "Physics", "Mathematics", "Additional Mathematics", "Chinese", "English", "Geography"],
  "terms": {
    "1": { "Biology": null, "Chemistry": null, ... },
    "2": { "Biology": null, "Chemistry": null, ... },
    "3": { "Biology": null, "Chemistry": null, ... },
    "4": { "Biology": null, "Chemistry": null, ... }
  },
  "maxScore": 100
}
```

## Calculations

### Running Average (after Term 2)
Sum of Term 1 + Term 2 scores / 2 for each subject.

### Target for A* (remaining terms)
The user can ask: *"What do I need on average in Terms 3 & 4 to get an A\* overall?"*

Formula:
```
Remaining Total Needed = (AStarThreshold × 4) - (T1 + T2)
Average per remaining term = Remaining Total Needed / 2
```

Where A\* threshold defaults to 90% of max score. If max is 100, A\* = 90.

Example: T1=85, T2=78, max=100
```
Remaining = (90 × 4) - (85 + 78) = 360 - 163 = 197
Avg per term = 197 / 2 = 98.5
```
Flag if remaining > max × 2 (impossible) or remaining ≤ 0 (already achieved).

### Year-End Average (with projection)
If user asks, show:
- Current average (T1+T2)/2
- If they hit the target average in T3+T4, what the final average would be

## Output

Always produce a **sorted table** (default: by current average descending).

| Subject | T1 | T2 | Avg | Grade | T3+T4 Target Avg | Status |
|---------|----|-----|-----|-------|------------------|--------|
| Physics | 85 | 78  | 81.5 | B | 98.5 | ⚠️ Tough |

### Sorting options:
- By current average (default, descending)
- Alphabetical
- By target difficulty (easiest to hardest)

### Default Grade Boundaries:

| Grade | Range |
|-------|-------|
| A*    | 90-100 |
| A     | 80-89 |
| B     | 70-79 |
| C     | 60-69 |
| D     | 50-59 |
| E     | 40-49 |
| F     | Below 40 |

Allow custom grade boundaries.

### Status column:
- ✅ **Achieved** — already at A\* average overall
- 🎯 **Reachable** — target avg ≤ max
- ⚠️ **Tough** — target avg close to max (≥95)
- ❌ **Impossible** — target avg > max

## Workflow

1. Check if `exam-scores.json` exists. Load existing data.
2. Accept new scores, merge into the record.
3. Calculate running averages for subjects with 2 terms of data.
4. Calculate T3+T4 target average for A\* where requested.
5. Sort and display as a table.
6. Save updated data.

## Validation

- Reject negative scores or scores > max
- Flag suspicious inputs
- If max not specified, assume 100
- If score already recorded for a term, ask before overwriting
