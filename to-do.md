# 🦀 Group7 To-Do Ability

A Discord-based to-do system with **multiple lists**. Anyone in the group can create lists, add tasks to specific lists, assign, set deadlines, and mark done. The claw tracks everything in `to-dos.json`.

## Commands

All commands use `@Group7 <command>` in the `#group-7` channel.

### Add a to-do
```
@Group7 add to-do: <description>
@Group7 add to-do: <description> | assign: <name>
@Group7 add to-do: <description> | by: YYYY-MM-DD
@Group7 add to-do: <description> into <list name>
@Group7 add to-do: <description> into <list name> | assign: <name>
@Group7 add to-do: <description> | assign: <name> | by: YYYY-MM-DD
@Group7 add to-do: <list name>: <description>
```
- `into <list name>` or `<list name>:` prefix adds the task to a specific list (e.g. `into homework` or `homework:`). If the list doesn't exist, it's created automatically.
- If no list is specified, the task goes to the **main** list.
- `assign:` assigns the task to someone
- `by:` sets a deadline in YYYY-MM-DD format
- Reply: `@Name ✅ received: <description> (in <list>)`

### List to-dos
```
@Group7 list to-dos
@Group7 list <list name>
@Group7 list all
```
- `list to-dos` or `list main` — shows the **main** list
- `list <name>` — shows a specific list (e.g. `list homework`)
- `list all` — shows all lists and their pending tasks

### Mark as done
```
@Group7 done <id>
@Group7 complete <id>
@Group7 mark done <id>
```
- Marks the to-do with that ID as completed
- Reply: `@Name ✅ <description> marked done!`

### Assign / Reassign
```
@Group7 assign <id> to <name>
@Group7 deadline <id> YYYY-MM-DD
```
- Assigns an existing to-do to someone
- `deadline` sets or updates the deadline

### List management
```
@Group7 list all lists
@Group7 what lists
```
- Shows all available list names

## Storage

- **Ability file:** `to-do.md` (this file)
- **Data file:** `to-dos.json` (persistent JSON storage)

## Data format

```json
{
  "lists": {
    "main": [
      {
        "id": 1,
        "description": "do the thing",
        "assignee": "alice",
        "deadline": "2026-06-20",
        "status": "pending",
        "created_by": "bob",
        "created_at": "2026-06-17T07:53:00Z"
      }
    ],
    "homework": [...]
  },
  "nextId": 2
}
```

- Lists are created on first use when a task is added with `into <newlist>`
- `deadline` is optional
- Completed tasks stay in the file but are filtered from listings

## Access Control

Only the following users can add, edit, or delete tasks in any list:
- `hannah`
- `sushi` (𝕊𝕦𝕤𝕙𝕚)
- `nc` (nc_0713)
- `mynyen`
- `shaun`
- `Korneliuz`

Members of `#sandbox-unit4` are **explicitly blocked** from modifying any list. They can view lists on request but cannot add, edit, assign, or complete tasks.

The claw checks the sender's display name or username against this list before accepting any write operation.

## Rules

- Task IDs auto-increment across all lists
- Listing shows only incomplete tasks by default
- Completed tasks remain in the file but are excluded from lists
- Only the original creator or an assigned person can mark a task done
- When listing by deadline, tasks sort soonest → latest
