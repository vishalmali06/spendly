# Spec: Registration

## Overview
Add full registration handling so a visitor can create a Spendly account from the existing `register.html` form. This step turns the current `GET /register` page into a working sign-up flow: it accepts a POST submission, validates the input, hashes the password with werkzeug, inserts a new row into the `users` table, On success the user is shown with a sucess message and then redirects to the login page on success. Registration is the first authenticated-user feature on the roadmap and unlocks every later step (login, profile, expenses CRUD).

## Depends on
- Step 1 — Database Setup (users table, `get_db()`, FK pragma) must be complete. It is.

## Routes
- `POST /register` — handle submitted registration form, validate, create user, redirect to `/login` on success — public
- `GET /register` — already implemented; will be updated only to render server-side errors and re-populate form fields — public

## Database changes
No schema changes. The `users` table from Step 1 already has `id`, `name`, `email`, `password_hash`, `created_at` and `email` is `UNIQUE NOT NULL`. A new helper `create_user(name, email, password)` will be added to `database/db.py` — this is a code change, not a schema change.

## Templates
- **Create:** none
- **Modify:**
  - `templates/register.html` — keep `{% if error %}` block, add re-population of `name` and `email` via `{{ form.name }}` / `{{ form.email }}` so a failed submit doesn't wipe valid fields
  - `templates/base.html` — add a flash message region above `{% block content %}` so the success message shown on `/login` after redirect is visible (uses `get_flashed_messages(with_categories=true)`)

## Files to change
- `app.py` — add `POST /register` handler; import `redirect`, `url_for`, `flash`, `request`, `abort` as needed; configure `app.secret_key` if not already set (required for `flash`)
- `database/db.py` — add `create_user(name, email, password)` and `get_user_by_email(email)` helpers
- `templates/register.html` — re-populate fields on error (see Templates above)
- `templates/base.html` — render flashed messages

## Files to create
- None

## New dependencies
No new dependencies. Werkzeug 3.1.6 is already in `requirements.txt` and `generate_password_hash` is already imported in `database/db.py`.

## Rules for implementation
- No SQLAlchemy or ORMs — use `sqlite3` via `get_db()` only
- Parameterised queries only — never f-string user input into SQL
- Passwords hashed with `werkzeug.security.generate_password_hash` before insert; never store plaintext
- Use CSS variables — never hardcode hex values in any style change
- All templates extend `base.html`
- Route lives in `app.py` only — no blueprints
- All DB access goes through helpers in `database/db.py` — no `sqlite3` calls inline in the route
- Use `url_for()` for every redirect/link — never hardcode `/login` or `/register`
- Use `flash()` + `redirect(url_for('login'))` on success; re-render `register.html` with `error=...` and form values on failure (do not redirect on error — preserves entered fields without sessions)
- Validation rules:
  - `name` — required, stripped, 1–80 chars
  - `email` — required, stripped, lowercased, must contain `@` and `.`, 5–120 chars
  - `password` — required, minimum 8 chars
  - duplicate email — catch via `get_user_by_email()` before insert (or catch `sqlite3.IntegrityError` from the `UNIQUE` constraint as a backstop)
- On unexpected DB errors, `abort(500)` rather than returning a string
- Set `app.secret_key` from an environment variable with a dev fallback — do not commit a hardcoded production secret

## Definition of done
Verifiable by running `python app.py` (port 5001) and `pytest`:

- [ ] `GET /register` renders the form and returns 200
- [ ] `POST /register` with valid `name`, `email`, `password` (≥8 chars) creates a row in `users` with a werkzeug-hashed `password_hash`, then 302-redirects to `/login`
- [ ] After the redirect, `/login` shows a flashed success message ("Account created — please sign in.")
- [ ] `POST /register` with a duplicate email re-renders `register.html` with an error message and 200 status; no second row is inserted
- [ ] `POST /register` with missing/invalid `name`, `email`, or `password` re-renders `register.html` with an error message and the previously entered `name` and `email` still populated (password field is not re-populated)
- [ ] No raw SQL string interpolation anywhere — all queries use `?` placeholders
- [ ] `password_hash` in the DB starts with `scrypt:` or `pbkdf2:` (werkzeug default), not the plaintext password
- [ ] `flask` dev server starts cleanly on port 5001 with no new pip packages added to `requirements.txt`
- [ ] All existing tests still pass; new tests cover the success path, duplicate email, and at least one validation failure
