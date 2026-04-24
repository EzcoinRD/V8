# EZ Coin Laundry Streamlit App — Priority Update

This package builds on the April 21, 2026 evening baseline version.

## Priority updates included

1. Purchases/Refunds now display on-screen in a visible daily table.
2. Phone-friendly layout improvements:
   - wider single-column feel
   - larger buttons
   - less reliance on sidebars
   - tighter mobile spacing
3. Reduced timeout/rerun pressure:
   - most entry workflows now save through forms
   - repeated database reads use short TTL caching
4. Session-state improvements:
   - product quantities stay stable while editing the cart
   - counter pages maintain values until saved or changed
5. Caching:
   - products, summaries, and reports use Streamlit cache_data with short TTLs
   - cache clears after database writes
6. Reopen-day behavior remains protected:
   - line-item detail stays in place
   - closing a reopened day replaces prior closeout status so it does not double-count

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

## Compact iPhone Layout Update

This version keeps the selected business day and inventory adjustment logic, but changes the product entry page to a compact phone layout:

- Smaller buttons and tighter spacing to reduce scrolling.
- Product name, price, minus, quantity, and plus controls fit on one compact row.
- Added a product filter/search box to quickly find an item.
- Reduced oversized mobile card spacing from the prior iPhone layout pass.
- App page layout is centered instead of wide.

Upload `app.py`, `requirements.txt`, and `README.md` to GitHub, replacing the existing files.
