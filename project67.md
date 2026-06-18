# PROJECT 67 — SENTRY (Product Specification)

## Product Overview

**Name:** SENTRY
**Tagline:** Project manager that never misses the signal.
**Target Audience:** Teams working on DSTA projects — members and executive committee members who need to keep track of updates, tasks, and logistics across large projects.
**Problem Statement:** How can we create an interactive project manager for members and executive committee of large projects that can make updates, new information and tasks easier to overview?

## Core Functions

### 1. Crisis Information Triage
Summarise incoming updates and flag what needs attention.

- Monitor incoming messages/chats/emails for urgent signals
- Flag items that teammates highlighted as critical ("THIS IS SUPER IMPORTANT GUYS")
- Alert user to urgent changes in project status
- Surface pinned messages and important announcements
- Check logistics — confirm whether items have been procured/purchased when prompted

### 2. Ops-Readiness & Task Tracking
Track tasks, missing items, status, and follow-ups.

- Maintain a task board with PENDING / IN PROGRESS / COMPLETE / BLOCKED
- Sort to-do list by priority and urgency automatically
- Track missing items required for project milestones
- Flag overdue items and dependencies
- Follow up on pending tasks

### 3. Chat Summarisation
Keep teams aligned without reading every message.

- Summarise chat history on demand
- Highlight key decisions, action items, and deadlines
- Extract what teammates pinned or flagged as super important

### 4. Spreadsheet Integration
Connect project logistics to a live spreadsheet.

- Link to Excel/Google Sheets for tracking missing items
- SENTRY can check the spreadsheet when prompted
- SENTRY can update the spreadsheet with new entries when directed

## How It Works

```
Incoming Updates ──► SENTRY ──► Structured Brief
  (chats,             │           - Priority
   emails,            │           - What changed
   spreadsheets,      │           - Action needed
   pinned messages)   │           - By when
                      │
                      ├──► Task Board (auto-sorted by urgency)
                      │
                      ├──► Logistics Check (spreadsheet lookups)
                      │
                      └──► Alert (if urgent)
```

## Product Name

[Product name pending — user to confirm]

---

**Last updated:** 2026-06-18
**Classification:** Group 7 Internal — Hannah's personal reference
**File:** project67.md
