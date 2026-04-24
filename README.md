# EZ Coin Laundry App - Landing Page Date Selector Update

This update is based on the selected business day + inventory adjustment version.

## What changed

- The full business-day date selector now appears on the Main Menu / landing page only.
- The app still defaults to the current day.
- The selected business day remains active as the user moves through the app.
- Subpages show the active business day and day status as a small label, but do not show the full date picker.
- Sales, bathroom entries, customer counts, change given, purchases/refunds, Daily Overview, Close Day, reopen-day logic, Inventory Received, and Inventory Adjustments continue to use the active selected business day.
- Selected-day closed/open protection remains in place.
- Inventory Adjustments and transaction-log inventory calculation remain in place.

## Files

Upload these files to GitHub:

- `app.py`
- `requirements.txt`
- `README.md`

## Notes for Codex handoff

Next recommended Codex task:

Review this Streamlit laundromat app and continue improving usability without removing the selected business-day workflow. Keep the date selector on the Main Menu only. Subpages should display the active business day clearly but should not include a full date picker. Preserve closed-day protection, reopen-day logic, inventory adjustments, purchases/refunds display, bilingual support, and cumulative export.
