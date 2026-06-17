# 🦀 Group7 To-Do Ability

A Discord-based to-do system. Anyone in the group can add, list, assign, and complete tasks. The claw tracks everything in `to-dos.json`.

## Commands

All commands use `@Group7 <command>` in the `#group-7` channel.

### Add a to-do
```
@Group7 add to-do: <description>
@Group7 add to-do: <description> | assign: <name>
```
- If `assign:` is included, the task is assigned to that person
- If omitted, the task is unassigned
- Reply: `@Name ✅ received: <description>`

### List to-dos
```
@Group7 list to-dos
@Group7 outstanding to-dos
@Group7 show to-dos
```
- Shows all incomplete to-dos with ID, description, assignee, and status

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
```
- Assigns an existing to-do to someone

## Storage

- **Ability file:** `to-do.md` (this file)
- **Data file:** `to-dos.json` (auto-created, append-only tasks list)

## Data format

Each to-do is stored as:
```json
{
  "id": 1,
  "description": "do the thing",
  "assignee": "alice",
  "status": "pending",
  "created_by": "bob",
  "created_at": "2026-06-17T07:53:00Z"
}
```

## Rules

- Task IDs auto-increment
- Listing shows only incomplete tasks by default
- Completed tasks stay in the file but are filtered out of lists
- Only the original creator or an assigned person can mark a task done
