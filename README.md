# EZ Coin Laundry App - iPhone Layout Update

This package updates the selected-business-day and inventory-adjustment version of the EZ Coin Laundry Streamlit app with a dedicated iPhone/mobile layout pass.

## Main improvements in this version

- Changed Streamlit layout from wide to centered for better phone display.
- Added stronger mobile CSS for larger tap targets, rounded buttons, and tighter spacing.
- Redesigned the global header so the selected business day, day status, user, language toggle, Main Menu, and Logout are easier to use on a phone.
- Redesigned the Product entry screen so each product appears as a simple phone-friendly row:
  - Product name
  - Price
  - Large minus button
  - Large quantity display
  - Large plus button
- Changed the Sale Summary screen to show phone-readable cards first, with the full table tucked into an expander.
- Changed Daily Overview, Purchases/Refunds, Inventory Received, Inventory Adjustments, and related activity sections to show card-style previews before full tables.
- Kept the selected business day workflow:
  - Defaults to the current day.
  - Allows selecting another business day.
  - Keeps the selected day active across pages.
- Kept closed-day protection and reopen logic.
- Kept inventory adjustments as an audit-trail transaction log.

## Files

- `app.py` - Main Streamlit app
- `requirements.txt` - Python dependencies for Streamlit Cloud
- `README.md` - This guide

## Demo logins

- Admin: `admin` / `admin123`
- Editor: `editor` / `editor123`
- Viewer: `viewer` / `viewer123`

## GitHub update steps

1. Upload/replace these files in your existing GitHub repository:
   - `app.py`
   - `requirements.txt`
   - `README.md`
2. Commit the change with a message such as:
   - `iPhone layout update`
3. Let Streamlit Cloud redeploy automatically, or reboot the app from Streamlit Cloud if needed.

## Notes

This version was syntax-checked with Python compile. It was not fully browser-tested inside Streamlit Cloud from this environment. If Streamlit shows an error after deployment, copy the full error message and use it to troubleshoot the next patch.
