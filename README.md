# Lafont Flowers Store

E-commerce style Django application for managing and browsing flower products, with authentication, catalog filtering, cart handling, and contact form email notifications.

## Tech Stack

- Python
- Django 5.x
- SQLite (default local database)

## Project Structure

```text
Store/
|- manage.py
|- db.sqlite3
|- Lafont_Flowers/        # Project config (settings, root urls, wsgi/asgi)
|- store/                 # Main app (models, views, forms, templates, static)
```

## Features

- User authentication
- Register, login, logout
- Customer profile record creation on user registration

- Product catalog
- Product listing and detail page
- Filtering by product type, color, search term, and price range

- Cart flow (session-based)
- Add products to cart
- Update quantity and remove products
- Cart totals computed from pack prices

- Contact flow
- Contact form with intent selection
- Sends one email to business and one confirmation email to the user

- Admin
- Standard Django admin available at `/admin/`

## Data Model Summary

Core models in `store/models.py`:

- `Product`
- Fields include name, type, unit price, color, available quantity, image URL, and flower-specific packaging fields
- Validation enforces that flower products require `grade`, `pack_quantity`, and `pack_unit`

- `FeaturedProducts`
- Links featured items to `Product`

- `Customer`
- Linked optionally to Django `User`
- Stores name, email, address, and phone

- `Order`
- Linked to `Customer`
- Stores purchase date, total, and status

- `OrderDetail`
- Links `Order` and `Product`
- Stores quantity and captured unit price at purchase time

## URL Overview

Root project routes:

- `/admin/`
- `/store/` (includes app routes)

App routes in `store/urls.py`:

- `/store/` - Home
- `/store/catalog/` - Catalog
- `/store/product/<id>/` - Product detail
- `/store/cart/` - Cart
- `/store/add-to-cart/<id>/` - Add product to cart
- `/store/checkout/` - Checkout template
- `/store/confirmation/<id>/` - Confirmation template
- `/store/register/` - Register
- `/store/login/` - Login
- `/store/logout/` - Logout
- `/store/profile/` - Profile template
- `/store/about/` - About template
- `/store/contact/` - Contact form

## Local Setup

1. Create and activate a virtual environment.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies.

```powershell
pip install -r requirements.txt
```

3. Apply migrations.

```powershell
python manage.py migrate
```

4. (Optional) Create an admin user.

```powershell
python manage.py createsuperuser
```

5. Run the development server.

```powershell
python manage.py runserver
```

6. Open:

- `http://127.0.0.1:8000/store/`
- `http://127.0.0.1:8000/admin/`

## Environment Variables (.env)

1. Create your local `.env` file from `.env.example`.

```powershell
Copy-Item .env.example .env
```

2. Edit `.env` and set at least:

- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `STRIPE_PUBLIC_KEY`
- `STRIPE_SECRET_KEY`

3. Never commit `.env` to git. The project `.gitignore` already excludes it.

## Stripe Test Mode (Local)

- Use Stripe test keys (`pk_test_...`, `sk_test_...`).
- Use test card: `4242 4242 4242 4242`, any future date, any CVC.

## Deploying to Hostinger (Recommended: VPS)

Hostinger shared web hosting is optimized for PHP. For Django + Stripe, a VPS plan is recommended.

1. Upload project and create virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set production environment variables in server panel or shell:

- `DEBUG=False`
- `SECRET_KEY=<strong-random-secret>`
- `ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com`
- `CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com`
- `STRIPE_PUBLIC_KEY=pk_live_...`
- `STRIPE_SECRET_KEY=sk_live_...`

4. Run migrations and collect static files:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

5. Serve with Gunicorn behind Nginx (or Hostinger Python app service if available for your plan).

6. In Stripe Dashboard, add your production domain to allowed return URLs and test live checkout flow.

## Email Configuration

Contact form email settings are read from environment variables in `Lafont_Flowers/settings.py`.

Available variables:

- `EMAIL_BACKEND`
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `EMAIL_USE_TLS`
- `DEFAULT_FROM_EMAIL`
- `CONTACT_RECEIVER_EMAIL`

If no environment variables are set, the app defaults to Django's console email backend in local development.

## Notes

- Database is SQLite by default (`db.sqlite3`).
- Some pages currently use template placeholders (`about`, `profile`, `checkout`, `confirmation`).
- Dependencies are defined in `requirements.txt`.
