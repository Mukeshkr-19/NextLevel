# Next Level Event Platform

This repository contains the Next-Level Leadership event web app. The current prototype keeps the original Flask and MongoDB flow available while adding safer event-day operations:

- team login and game scoring,
- live leaderboard,
- staff admin dashboard,
- manual score adjustments with required reasons,
- score audit history,
- CSV export for backups,
- Docker-based local deployment.

The main goal is event-day reliability. Cloud deployment and UI polish come after the local event workflow is stable and tested.

## Branch workflow

- `main` is the production/fallback branch.
- `dev` is the integration branch for the safer prototype.
- Feature work happens on a focused branch, then merges into `dev` only after verification.
- Do not merge to `main` until the prototype has been tested and approved for production use.

## Local setup

Install Python dependencies in a virtual environment:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

The app expects MongoDB at host `mongo` when running in Docker. For normal event testing, use the Docker workflow below.

## Admin PIN

The admin dashboard is disabled until `NEXTLEVEL_ADMIN_PIN` is set.

For local testing only:

```bash
export NEXTLEVEL_ADMIN_PIN=1234
```

Use a different PIN for any real event run. Do not commit event PINs, credentials, or secrets.

## Docker run

Docker is used for milestone verification and event-style local runs. It does not need to run after every small edit.

If Colima is stopped:

```bash
colima start
```

Build and run the app with MongoDB:

```bash
docker network create nextlevel-net
docker run -d --name nextlevel-mongo --network nextlevel-net mongo:4.2.5
docker build -t nextlevel-app .
docker run -d --name nextlevel-app --network nextlevel-net -p 3000:3000 -e WAIT_HOSTS=mongo:27017 -e NEXTLEVEL_ADMIN_PIN=1234 nextlevel-app
```

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

## Lightweight checks

Run these before commits:

```bash
python3 -m py_compile main.py helpers.py
python3 -m unittest discover -s tests
git diff --check
```

Run Docker verification at milestones, before demos, and before merging to `dev`.

## Accessibility note

Public-facing pages must be reviewed before they are considered ready for event use. Use the project accessibility checklist and target WCAG-style AA checks. Do not claim legal ADA compliance without proper review.

Gallery and public photo changes need extra discussion before release because image descriptions, keyboard access, and layout can affect accessibility.

## Important files

- `main.py`: Flask routes, scoring, leaderboard data, admin routes.
- `templates/admin.html`: staff dashboard.
- `templates/leaderboard.html`: projector-friendly leaderboard.
- `EVENT_RUNBOOK.md`: event-day operating guide.
- `ACCESSIBILITY_CHECKLIST.md`: public-facing review checklist.
- `DEVELOPMENT_PLAN.md`: next prototype tracks and priorities.
