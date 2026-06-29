# Development Plan

This plan keeps the modernization safe: reliability first, accessibility second, simplicity third, cloud polish fourth.

## Track A: Backend and admin reliability

Current focus.

- Keep the original team login and gameplay behavior available.
- Improve staff admin workflows.
- Add tests for scoring, audit logs, CSV export, and leaderboard ranking.
- Add backup and export procedures.
- Add event setup/reset tools only after the current admin workflow is stable.
- Keep implementation simple enough for future student maintainers.

Next priorities:

1. Add lightweight tests for admin score adjustment and CSV export.
2. Improve admin dashboard wording and error handling.
3. Add a safe event setup checklist to the admin page or docs.
4. Add database backup notes before any live event.

## Track B: Public-facing accessibility-gated work

Move more slowly here.

- Review leaderboard accessibility after visual changes.
- Review game page labels and question workflow.
- Improve public pages only after checking keyboard access, focus, image alt text, contrast, and responsive behavior.
- Do not make major gallery changes until the accessibility approach is discussed.

Next priorities:

1. Run the accessibility checklist against the leaderboard.
2. Review game form labels and instructions.
3. Decide how the photo gallery should work before adding upload or cloud storage.

## Track C: Cloud and resume readiness

Do after the local event workflow is stable.

- Document environment variables.
- Prepare for managed MongoDB.
- Add backup/export procedure for cloud.
- Compare simple hosting options.
- Keep deployment boring and reliable.

Possible later stack:

- Render, Railway, or Fly.io for Flask.
- MongoDB Atlas for managed database.
- Object storage only if gallery uploads become part of the approved scope.

## Prototype definition of done

- Admin staff can view teams and scores.
- Staff can adjust points with a required reason.
- Audit history records manual changes.
- Scores can be exported to CSV.
- Leaderboard has rank, tie handling, points, and last-updated information.
- Documentation explains setup, event operation, fallback, and accessibility review.
- Lightweight checks and relevant tests pass.
- Docker integration check passes at a milestone.
- Docker/Colima are stopped after testing.
- Branch is pushed to the fork and not merged to `dev` until approved.
