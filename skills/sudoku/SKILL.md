# Sudoku Skill

When asked for a sudoku, follow these steps:

## 1. Decide the delivery method

| Context | What to do |
|---------|-----------|
| Webchat / Canvas | Generate an interactive HTML sudoku board inline in the canvas |
| Terminal | Run `sudoku.fetcher` script to fetch + print ASCII grid |
| Vague ("open sudoku") | Open https://sudoku.com in the browser |

## 2. Fetcher script

Located at `~/.openclaw/workspace/skills/sudoku/sudoku.fetcher`

Fetches from `https://sudoku-api.vercel.app/api/dosuku` and prints a 9×9 ASCII grid.

## 3. Inline HTML grid (canvas/web)

Generate a 9×9 grid:
- Locked cells = the given clues (disabled input, bold)
- Empty cells = editable `<input>` fields
- Include a "Check" button that highlights wrong answers in red
- Clean, minimal styling, add a "New Puzzle" button

## Files

- `SKILL.md` — This file
- `sudoku.fetcher` — Bash script to fetch + display
