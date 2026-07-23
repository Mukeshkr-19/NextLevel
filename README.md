# Next Level Event Platform

Next Level is a Flask and MongoDB web app for the annual Next-Level Leadership event. It supports team login, event questions, score tracking, a live projector leaderboard, and staff score administration.

This branch is a safer prototype for the 2026-27 event cycle. The priority is event-day reliability first, cloud readiness second, and UI polish third.

## Current Prototype

The prototype keeps the original app available as a fallback and adds:

- staff admin dashboard for teams and scores,
- manual score adjustments with required reasons,
- score audit history,
- CSV score export for backups,
- rank and tie handling on the leaderboard,
- last-updated data for staff/projector use,
- public-page accessibility review notes,
- Docker-based local run path,
- event-day runbook and backup guidance.

This is not final production hosting yet. Use it as a working prototype until the event team approves the workflow and deployment plan.

## Branch Workflow

- `main`: production/fallback branch.
- `dev`: integration branch for tested event-cycle work.
- `YYYY-YY-nextlevel`: one active event-cycle branch, such as `2026-27-nextlevel`.

Yearly work should start from `dev`, use a Git-safe branch name like `2026-27-nextlevel`, and keep all changes for that event cycle on that branch. After verification, merge the yearly branch into `dev`. Merge `dev` into `main` only after the event workflow is tested and approved for production/fallback use.

Do not keep old temporary feature branches after their work has moved into the yearly branch. They make handoff harder for the next student or staff maintainer.

Recommended handoff rule:

1. Pull the latest `dev`.
2. Create or switch to the yearly branch, for example `2026-27-nextlevel`.
3. Make and verify changes on the yearly branch.
4. Push the yearly branch to GitHub.
5. Merge yearly branch into `dev` after checks pass.
6. Merge `dev` into `main` only after staff approval.

## Requirements

- Python 3
- Docker
- Colima on macOS, if Docker Desktop is not used
- MongoDB, provided by Docker for local testing

## Local Development Setup

Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

Run local checks before committing:

```bash
python3 -m py_compile main.py helpers.py
python3 -m unittest discover -s tests
git diff --check
```

## Admin PIN

The admin dashboard requires `NEXTLEVEL_ADMIN_PIN`.

For local testing only:

```bash
export NEXTLEVEL_ADMIN_PIN=1234
```

Use a different PIN for any real event run. Do not commit event PINs, passwords, exported credentials, or secrets.

## Docker Demo Run

Start Colima if needed:

```bash
colima start
```

Build and run the app with MongoDB:

```bash
docker network create nextlevel-net
docker run -d --name nextlevel-mongo --network nextlevel-net --network-alias mongo mongo:4.2.5
docker build -t nextlevel-app .
docker run -d --name nextlevel-app --network nextlevel-net -p 3000:3000 -e WAIT_HOSTS=mongo:27017 -e NEXTLEVEL_ADMIN_PIN=1234 nextlevel-app
```

If old demo containers already exist:

```bash
docker rm -f nextlevel-app nextlevel-mongo
```

Then run the MongoDB and app commands again.

Open:

- Main site: <http://127.0.0.1:3000>
- Admin login: <http://127.0.0.1:3000/admin/login>
- Leaderboard: <http://127.0.0.1:3000/leaderboard>

Stop containers after testing:

```bash
docker stop nextlevel-app nextlevel-mongo
docker rm nextlevel-app nextlevel-mongo
docker ps
colima stop
```

## Staff Demo Flow

1. Open the main site and leaderboard.
2. Log in to `/admin/login`.
3. Confirm teams are visible in the admin dashboard.
4. Adjust a team's score with a clear reason.
5. Confirm the audit log records the change.
6. Confirm the leaderboard updates with rank, team, and points.
7. Export the CSV backup.

Recommended explanation:

```text
The current system stays available as a fallback. This prototype adds staff-friendly score corrections, required reasons, audit history, CSV backups, and a clearer projector leaderboard so event-day scoring is easier to recover and explain.
```

## Event-Day Operating Notes

Before using this at a live event:

- run Docker verification on the event laptop,
- confirm the admin PIN is set outside the repo,
- export an initial CSV backup,
- keep a manual score sheet ready,
- assign one scorekeeper and one technical helper,
- review public pages using the accessibility checklist.

See `EVENT_RUNBOOK.md` for the full staff runbook.

## Accessibility

Public-facing pages have an initial accessibility checklist review. Current focus areas include keyboard focus, clearer form instructions, semantic leaderboard tables, and pauseable leaderboard updates.

Do not describe the project as legally ADA-certified without formal review.

## Important Files

- `main.py`: Flask routes, scoring, leaderboard data, admin routes.
- `helpers.py`: shared helper functions.
- `templates/admin.html`: staff dashboard.
- `templates/admin_login.html`: admin login page.
- `templates/game.html`: team game page.
- `templates/leaderboard.html`: projector leaderboard.
- `tests/test_admin_workflow.py`: admin, leaderboard, export, and accessibility smoke tests.
- `EVENT_RUNBOOK.md`: event-day operating guide.
- `ACCESSIBILITY_CHECKLIST.md`: public-page review checklist.
- `ACCESSIBILITY_REVIEW.md`: current accessibility review notes.
- `DEVELOPMENT_PLAN.md`: planned prototype tracks.

## Deployment Direction

The near-term goal is a stable local/Docker prototype. Later cloud deployment can use a managed app host plus managed MongoDB, such as Render, Railway, Fly.io, or a similar service with MongoDB Atlas.

Before any live cloud deployment, add a tested backup/export process, production secret handling, and a rollback plan.
