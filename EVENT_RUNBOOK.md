# Event Runbook

This guide is for staff and student helpers running the Next-Level Leadership event app.

## Roles

- Event lead: decides when the system is ready for participants.
- Scorekeeper: uses the admin dashboard to review and correct scores.
- Technical helper: starts/stops the app, exports backups, and watches for errors.
- Manual backup helper: keeps a paper or spreadsheet score copy during the event.

## Before the event

1. Confirm the event laptop is charged and connected to reliable power.
2. Confirm the app runs locally in Docker.
3. Confirm the admin PIN is set and known only to trusted staff.
4. Open the main site, game page, leaderboard, and admin login.
5. Confirm registered teams appear in the admin dashboard.
6. Export an initial CSV backup from `/admin/export/scores.csv`.
7. Open the leaderboard on the projector screen.
8. Keep a manual score sheet ready as fallback.
9. Confirm who is allowed to make score corrections.
10. Confirm public-facing pages have had an accessibility review before use.

## During the event

1. Keep the leaderboard open on the projector.
2. Keep the admin dashboard open for the scorekeeper.
3. Record any manual score adjustment with a clear reason.
4. Export CSV backups during natural breaks.
5. If teams report scoring issues, verify the team name and question before adjusting points.
6. Do not edit code or credentials during the event unless the system is unusable.
7. If the app becomes unreliable, switch to the manual score sheet and announce that staff are tracking scores.

## Score corrections

Use the admin dashboard:

1. Select the team.
2. Enter a positive or negative point adjustment.
3. Enter a plain reason, such as `mentor bonus verified` or `duplicate score removed`.
4. Enter the staff name if helpful.
5. Confirm the audit log shows the change.
6. Export a CSV backup after important corrections.

Point totals never go below zero. If a negative adjustment is larger than the team's score, the app records the actual change needed to reach zero.

## Emergency fallback

If the app disconnects or becomes unreliable:

1. Stop using the live leaderboard for official results.
2. Export the latest CSV if the admin dashboard is still reachable.
3. Continue scoring in the manual spreadsheet or paper sheet.
4. Record team name, point change, reason, and staff initials.
5. After the event, reconcile manual scores with the audit log and CSV exports.

## Backup/export steps

1. Log in at `/admin/login`.
2. Click `Export CSV`.
3. Save the file with the event date and time in the filename.
4. Keep at least one backup copy outside the event app folder.

Suggested filename:

```text
next-level-scores-YYYY-MM-DD-HHMM.csv
```

## After the event

1. Export the final CSV.
2. Save the final audit log view with screenshots if needed.
3. Stop app and database containers.
4. Stop Colima so the VM does not keep using memory.
5. Store final scores with the event files.
6. Write down any issues before they are forgotten.

## Stop local Docker

```bash
docker stop nextlevel-app nextlevel-mongo
docker rm nextlevel-app nextlevel-mongo
docker ps
colima stop
```
