# EZ Coin Laundry Streamlit App — Selected-Day + Inventory Adjustment Update

This package builds on the April 21, 2026 evening baseline version and the later priority update.

## New updates included in this package

1. Selected Business Day workflow
   - App defaults to the current Pacific Time day.
   - User can select another business day from the header on each page.
   - The selected day stays active while moving through the app.
   - Sales, bathroom entries, customer count, change given, purchases/refunds, inventory received, inventory adjustments, Daily Overview, Close Day, and reopen-day logic all use the selected business day.

2. Closed-day protection
   - If the selected business day is closed, entry screens prompt the user to reopen the day before making changes.
   - Admin can reopen from the prompt.
   - Non-admin users are told they need admin permission.
   - Reopen keeps line-item detail available and avoids double counting when the day is closed again.

3. Inventory Adjustments screen
   - Added a new admin-only Inventory Adjustments page.
   - Supports missed-day entries and inventory corrections.
   - Adjustment types include Count Correction, Damage / Spoilage, Theft / Loss, Found Inventory, Entry Correction, and Other.
   - Quantity change can be positive or negative.
   - Each adjustment stores business date, timestamp, product, quantity change, reason/type, notes, recorded by, and status.

4. Transaction-log inventory model
   - Inventory is calculated from history instead of directly overwriting totals.
   - Formula: opening inventory + inventory received - product sales +/- inventory adjustments = calculated on-hand inventory.
   - Inventory Received now adds receipt records and updates units-per-case only.
   - Product sales reduce calculated inventory through the sales transaction log rather than directly editing the product master.

5. Inventory Position table
   - Daily Overview and Inventory Adjustments show calculated inventory position.
   - Columns include opening inventory, received units, sold units, adjusted units, and calculated on-hand quantity.

## Prior priority updates retained

- Purchases/Refunds display on-screen in a visible daily table.
- Phone-friendly layout improvements.
- Larger buttons and tighter mobile spacing.
- Entry workflows use forms where practical.
- Product quantities stay stable in session state.
- Counter pages maintain values until saved.
- Short TTL caching is used for products, summaries, and reports.
- Cache clears after database writes.

## Default demo logins

- admin / admin123
- editor / editor123
- viewer / viewer123

Change these before using real store data.

## Deployment

Upload these files to your GitHub repository:

- app.py
- requirements.txt
- README.md

Then redeploy your Streamlit app with `app.py` as the main file.

## Local run

```bash
pip install -r requirements.txt
streamlit run app.py
```
