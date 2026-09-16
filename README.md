# CRATE — Redesigned E-commerce Store (Flask)

A restyled version of Task 1, same features, new look.

## What's different from v1
- Custom dark "workshop" theme instead of default Bootstrap look
- Monospace price tags on product cards (shelf-tag style)
- Signal-bar stock indicator instead of plain text
- Checkout / order confirmation styled as a torn receipt with a barcode
- Product detail page has a spec-sheet style info panel (SKU, price, stock)

## Features (same as before)
- Product listing (homepage) + product detail page
- Shopping cart (session-based)
- User registration & login (Flask-Login, hashed passwords)
- Checkout & order processing (saved to SQLite)
- Order history page
- Stock auto-decreases after checkout

## How to run it

1. Open a terminal in this folder.
2. (Recommended) Create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # Mac/Linux
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the app:
   ```
   python app.py
   ```
5. Open your browser at: http://127.0.0.1:5000

A `store.db` SQLite file is created automatically on first run, pre-filled
with 6 products (with real photos already wired up).

## Project structure
```
ecommerce-v2/
├── app.py                  <- backend logic (routes, models, DB)
├── requirements.txt
├── templates/               <- HTML pages
│   ├── base.html
│   ├── index.html
│   ├── product_detail.html
│   ├── cart.html
│   ├── checkout.html
│   ├── order_success.html
│   ├── my_orders.html
│   ├── login.html
│   └── register.html
└── static/
    ├── style.css             <- entire custom design system lives here
    └── images/                <- product photos
```

## Notes
- Fonts (Space Grotesk, Inter, JetBrains Mono) load from Google Fonts via CDN —
  needs internet the first time the page loads. If you're offline, the
  browser falls back to a default sans-serif, everything still works.
- Design tokens (colors, fonts, spacing) are all defined as CSS variables
  at the top of `style.css` under `:root` — change those to retheme the
  whole site from one place.
