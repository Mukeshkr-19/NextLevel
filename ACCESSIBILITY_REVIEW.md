# Accessibility Review Notes

Date: 2026-06-29

Scope:

- `templates/leaderboard.html`
- `templates/game.html`

Review target:

- WCAG-style AA checklist review for practical event readiness.
- This is not a legal ADA compliance claim.

## Changes made

- Added visible keyboard focus styling for links, buttons, and game inputs.
- Added accessible names for mobile navigation toggle buttons.
- Added a pause/resume control for leaderboard auto-refresh.
- Slowed leaderboard refresh from every second to every five seconds.
- Added a screen-reader-only leaderboard table caption.
- Added table column scopes for rank, team, and points.
- Escaped team names before rendering live leaderboard updates in JavaScript.
- Added game-page instructions explaining that teams enter staff-provided verification codes.
- Added field help text and `aria-describedby` relationships for game answer inputs.

## Checklist result

- Keyboard access: reviewed for changed controls.
- Focus visibility: improved on changed pages.
- Forms and labels: game inputs have visible labels and linked help text.
- Live updates: leaderboard updates can now be paused.
- Table semantics: leaderboard table has caption and scoped headers.
- Color contrast: no new low-contrast text was intentionally introduced.
- Motion/distraction: leaderboard refresh interval reduced and made controllable.

## Remaining review items

- Full keyboard walkthrough in a browser before demo.
- Visual check on projector-sized display.
- Screen reader behavior for live leaderboard updates if needed for the event audience.
- Broader public-page review for home, login, mentor/staff, and conference/gallery pages.
- Gallery requires separate discussion before major changes.

Recommended wording:

- `accessibility-reviewed against project checklist`
- `needs broader public-page review before event release`

Avoid saying this is legally ADA compliant unless the proper reviewer confirms it.
