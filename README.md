# SwampWorks Website

A Django club website built on the **django-quickstart** template. It adds a shared navbar, a club meetings calendar, a moderated projects gallery, an open project ideas board, and an admin area protected by a passkey.

## Stack

- Django 5.1 with a custom `accounts.User` model (extends `AbstractUser`)
- TailwindCSS via `django-tailwind` (the `theme` app), plus hand-written CSS per app
- SQLite in development (`DEBUG=True`), Postgres and AWS S3 in production (`DEBUG=False`)
- Pillow for image uploads

## Apps

| App | Purpose |
|---|---|
| `landing_page` | Public pages: home/about (calendar), projects, project ideas, contact |
| `accounts` | Sign up, log in, log out, and the admin passkey login |
| `dashboard` | Post-login page and the admin area (user management, project approvals) |
| `theme` | django-tailwind build output |

## Features

### Shared navbar
A single partial at `landing_page/templates/partials/navbar.html` is included by the `base.html` of every app, so it appears on every page (including login and sign up). It contains About Us, Projects, Project Ideas, Contact, and Sign Up. The login slot shows **Log In** for visitors and **Log Out** (plus an **Admin** link) once signed in. Styling lives in `landing_page/static/landing_page/css/navbar.css`.

### Sign up
The registration form (`CustomUserCreationForm`) asks for first name, last name, username, email, and password. First and last name are required. The admin "Add a user" form reuses the same form.

### Landing page and calendar
- `/` and `/about/` render the same page (both URLs point to the `index` view).
- The page shows a month-grid calendar of club meetings with Prev/Next navigation, plus an upcoming meetings list.
- Anyone can view it. Only an admin can add or delete meetings.
- Model: `ClubMeeting` (title, description, date, optional time).

### Projects
- Anyone, logged in or not, can submit a project (image and description) at `/projects/`.
- New submissions are saved with `is_approved=False` and are hidden from the public page.
- When a project is submitted, an email is sent to `ADMIN_EMAIL` linking to the admin area.
- An admin approves or rejects each pending project from the admin area. Approving makes it public. Rejecting deletes it.
- Each project has a **status** of Ongoing or Completed. Everyone can see the badge. Only an admin can change it.
- Model: `Project` (image, description, status, is_approved, created_at).

### Project ideas
`/ideas/` is a separate board where anyone can post a text-only idea with no login or approval. Model: `Idea` (description, created_at).

### Admin access
Admin access is a second step on top of a normal login:
1. Log in as a regular user.
2. Click **Admin** in the navbar and enter the passkey (`ADMIN_PASSKEY` in `.env`).
3. The session is flagged with `is_admin`, which unlocks admin-only actions (calendar editing, project status, approvals, and the admin area).

The flag lasts for the session and is cleared on logout. Every admin action is checked server-side, not just hidden in the templates.

### Admin area (`/dashboard/admin/`)
- **Pending Projects**: approve or reject submissions.
- **Users**: view username, email, staff status, and join date (never passwords), and delete users. Admins cannot delete their own account.
- **Add a user**: create accounts with the same validation as public sign up.

## URL map

| URL | Page |
|---|---|
| `/`, `/about/` | Landing page with calendar |
| `/projects/` | Projects gallery and submission form |
| `/ideas/` | Project ideas board |
| `/contact/` | Blank page |
| `/accounts/login/`, `/accounts/register/`, `/accounts/logout/` | Authentication |
| `/accounts/admin-login/` | Admin passkey entry (login required) |
| `/dashboard/` | Post-login page |
| `/dashboard/admin/` | Admin area (passkey required) |
| `/admin/` | Django's built-in admin site |

## Setup

```bash
python -m venv env
env\Scripts\activate          # Windows
pip install -r requirements.txt
pip install Pillow
python manage.py tailwind install
python manage.py makemigrations landing_page
python manage.py migrate
```

Run the two servers in separate terminals:

```bash
python manage.py tailwind start
python manage.py runserver
```

### Media uploads
Add to `settings.py`:

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

And at the bottom of the project `urls.py`:

```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

Consider adding `media/` to `.gitignore`.

### Environment variables (`.env`)

```
DEBUG="True"
SECRET_KEY="..."
ADMIN_PASSKEY="choose-a-strong-passkey"

# Project approval emails
ADMIN_EMAIL="where-notifications-go@example.com"
EMAIL_HOST="smtp.gmail.com"
EMAIL_PORT="587"
EMAIL_HOST_USER="sending-account@gmail.com"
EMAIL_HOST_PASSWORD="gmail-app-password"
EMAIL_USE_TLS="True"
DEFAULT_FROM_EMAIL="sending-account@gmail.com"
```

Settings read these with `os.environ.get(...)`: `ADMIN_PASSKEY`, `ADMIN_EMAIL`, and the `EMAIL_*` values.

### Sending real email
Gmail needs 2-Step Verification and an **App Password** (not your normal password). With `DEBUG=True`, the default backend only prints emails to the terminal. To send real email locally, set this in `settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
```

Do not set `DEBUG=False` just to send email, because that also switches the project to Postgres and S3.

## Notes and known limits

- `/ideas/` has no spam protection. Anyone, including bots, can post.
- Meetings can be added and deleted, but not edited.
- Rejected projects are deleted outright, not archived.
- `is_admin` is a per-session flag using one shared passkey, not a permanent role.
- Each `views.py`, `urls.py`, and `models.py` must be replaced in full when updating. Partial copies cause errors such as `module 'landing_page.views' has no attribute ...`.