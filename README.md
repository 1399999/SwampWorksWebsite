# SwampWorks

**SwampWorks Coding Club**: a platform that empowers coding club members to showcase their projects, manage ideas, and connect with the community through collaboration and resources.

Members post what they are working on, pitch ideas for what to build next, and meet regularly to code side by side. Browse the projects, add your own, or drop an idea for someone else to pick up.

> Built with Django and Bootstrap 5. Originally generated from the django-quickstart template (MIT), since refactored: Tailwind and the per-app CSS files were replaced by a shared Bootstrap layout.

---

## What's on the site

Each page's heading and intro text comes straight from the UI.

### Home / About Us (`/` and `/about/`)
*Coding Club: **SwampWorks***. The landing page introduces the platform and links to **View Projects** and **Share an Idea**.

- **Next meeting** card shows the soonest upcoming meeting (or "No meetings scheduled: check back soon").
- **About us: "Build together, learn together."** explains how the club works.
- **Club Meetings** is a month-grid calendar with Prev/Next navigation, plus an **Upcoming Meetings** list. Admins can add and delete meetings.

`/about/` serves the same page as `/` (the About section is anchored at `#about`).

### Projects (`/projects/`)
*What we build: "See what club members are working on, and add your own for the community to see."*

- **Current Projects** and **Previous Projects** are two sections, split by each project's status (ongoing or completed).
- Each project card shows a photo carousel, title, description, technology badges, and a team list with roles.
- **Add a project**: *"Submitted projects are reviewed by an admin before they appear here."* The form takes a title, description, technologies, photos, and team rows (*"Add everyone who worked on the project and their role. Leave unused rows blank."*). **Logged-in users only**; logged-out visitors see a Log In / Sign Up prompt instead.
- Admins also get a status dropdown, **Edit**, and **Delete project** on each card.

### Edit Project (`/projects/<id>/edit/`, admin only)
*Admin: Edit Project.* Change the title, description, technologies, and status. *"Tick a photo to remove it when you save"*, add more photos, and manage the team (*"Tick 'Remove' on a row to delete that person. Use the blank rows to add people."*). Cancel returns to where you came from.

### Project Ideas (`/ideas/`)
*What's next: "Have something you would like to see built? Share it here for the club to pick up."*

Anyone can read the ideas. Posting (**Share an idea**) needs a login. Admins can delete ideas.

### Contact Us (`/contact/`)
*Get in touch: "Questions about the club or the site? Reach out to any of our officers."*

A list of officers with role and a mailto link. Admins can add and remove contacts.

### Log In, Register, Admin Login (`/accounts/...`)
Centered card forms. Registration collects first name, last name, username, email, and password. **Admin Login** (reachable from the navbar's **Admin** link once logged in) asks for the admin passkey.

### Dashboard (`/dashboard/`)
*"Hi there, {username}. Welcome to the dashboard."* A login-restricted landing page for members, with a log out link.

### Admin Area (`/dashboard/admin/`)
*"Approve submitted projects and manage user accounts."*

- **Pending Projects**: Approve, Edit, or Reject each submission.
- **Users**: view username, email, staff status, and join date (never passwords); delete users (not yourself).
- **Add a user**: create accounts with the same validation as public sign up.

### Navbar and footer (every page)
- Navbar: **SwampWorks / Coding Club** brand; About Us, Projects, Project Ideas, Contact; **Log In** and **Sign Up** when logged out, **Admin** and **Log Out** when logged in. The current page is highlighted.
- Footer: *"Showcase projects, share ideas, and connect with the community."* with quick links, plus **SwampWorks Coding Club** and **Green Level High School's Coding club**.

---

## Who can do what

| | Visitor | Logged-in member | Admin (passkey) |
|---|---|---|---|
| View projects, ideas, contacts, calendar | yes | yes | yes |
| Submit a project (goes to approval) | no | yes | yes |
| Post an idea | no | yes | yes |
| Approve / reject / edit / delete projects, change status | no | no | yes |
| Delete ideas | no | no | yes |
| Add / delete calendar meetings | no | no | yes |
| Add / remove contacts | no | no | yes |
| View / add / delete users | no | no | yes |

Every restricted action is enforced in the view, not only hidden in the template.

### How admin access works
Admin is a second step on top of a normal login:
1. Log in as a regular user.
2. Click **Admin** in the navbar and enter the passkey (`ADMIN_PASSKEY` in `.env`).
3. The session is flagged `is_admin`, which unlocks the admin-only actions above. The flag ends on logout or when the session expires.

### How project approval works
1. A logged-in member submits a project. It is saved as unapproved and hidden from the public page.
2. An email goes to `ADMIN_EMAIL` linking to the admin area. Ideas also trigger a short email labeled as an idea.
3. An admin reviews it under **Pending Projects**, optionally edits it, then approves it (it appears under Current Projects) or rejects it (deleted).

---

## Code structure

```
swamp_works/            project settings and root URLs
accounts/               custom User model, login, register, logout, admin passkey login
dashboard/              post-login page and the admin area (users, pending projects)
landing_page/           public pages, calendar, projects, ideas, contacts
  templatetags/bootstrap_extras.py      add_class filter
  static/landing_page/css/theme.css     site theme on top of Bootstrap
  templates/landing_page/               base, index, about, projects, edit_project, ideas, contact
  templates/partials/                   navbar, footer, project_card, project_carousel
accounts/templates/accounts/            base, login, register, admin_login
dashboard/templates/dashboard/          base, index, admin
```

### The refactor
- **One look for the whole site.** Every page extends a `base.html` that loads Bootstrap 5.3.3 (CSS and JS from a CDN) and `theme.css`, and includes the shared navbar and footer. The three apps each have a `base.html` (landing page, accounts card layout, dashboard) that share the same partials.
- **No Tailwind and no per-app CSS.** The npm build, the `theme` app, and `django-tailwind` are gone; styling is Bootstrap utility classes plus the small `theme.css`. The old stylesheets (`reset.css`, `navbar.css`, `calendar.css`, `auth.css`, and so on) are no longer linked and can be deleted.
- **Reusable partials.** `navbar.html` and `footer.html` appear on every page. `project_card.html` renders a project everywhere it's listed (including admin controls), and `project_carousel.html` renders its photos. The admin area reuses both.
- **Forms rendered with one filter.** Templates load `bootstrap_extras` and use `{{ field|add_class:"form-control" }}` so Django forms pick up Bootstrap styling without custom widgets.
- **Shared layout.** `d-flex flex-column min-vh-100` on `<body>` keeps the footer at the bottom of short pages, and `base.html` has an `extra_head` block for page-specific head content.
- **Theme.** `theme.css` holds the palette (navy, lime green, and white) and overrides Bootstrap's primary, dark, and button colors.

### Data model (as the templates use it)
| Model | Fields |
|---|---|
| `Project` | title, description, technologies (comma-separated, exposed as `technology_list`), status (`ongoing` / `completed`), is_approved, created_at |
| `ProjectImage` | project, image (many per project; drives the carousel) |
| `ProjectMember` | project, name, role (the team list) |
| `Idea` | description, created_at |
| `ClubMeeting` | title, description, date, optional time |
| `Contact` | name, role, email |
| `accounts.User` | Django `AbstractUser` (first name, last name, username, email) |

### URL names the templates use
- `landing_page:` index, about, projects, edit_project, update_project_status, approve_project, reject_project, delete_project, ideas, delete_idea, contact, delete_contact, delete_meeting
- `accounts:` login, register, logout, admin_login
- `dashboard:` index, admin, admin_delete_user

---

## Setup

```bash
python -m venv env
env\Scripts\activate            # Windows (macOS/Linux: source env/bin/activate)
pip install -r requirements.txt
pip install Pillow              # needed for image uploads
python manage.py makemigrations landing_page
python manage.py migrate
python manage.py runserver
```

There is no second terminal or npm step any more. After adding a new template tag file, restart the server.

### Media uploads
`settings.py`:
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```
and at the bottom of the project `urls.py`:
```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```
Add `media/` to `.gitignore`. With `DEBUG=False` the project switches to Postgres and S3 (see the `if not DEBUG` blocks in `settings.py`).

### Environment variables (`.env`, next to `manage.py`)
```
DEBUG="True"
SECRET_KEY="..."
ADMIN_PASSKEY="choose-a-strong-passkey"

# Notification emails
ADMIN_EMAIL="where-notifications-go@example.com"
EMAIL_HOST="smtp.gmail.com"
EMAIL_PORT="587"
EMAIL_HOST_USER="sending-account@gmail.com"
EMAIL_HOST_PASSWORD="gmail-app-password"
EMAIL_USE_TLS="True"
DEFAULT_FROM_EMAIL="sending-account@gmail.com"
```
`settings.py` reads these with `os.environ.get(...)`: `ADMIN_PASSKEY = os.environ.get('ADMIN_PASSKEY')`, `ADMIN_EMAIL`, and the `EMAIL_*` values.

### Sending real email
Gmail needs 2-Step Verification and an **App Password**, not your normal password. With `DEBUG=True` the default email backend only prints to the terminal; to really send, set `EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'` in `settings.py`. Don't set `DEBUG=False` just to send email.

### If the admin passkey is rejected
Print what Django loaded: `python manage.py shell -c "from django.conf import settings; print(repr(settings.ADMIN_PASSKEY))"`. `None` means `.env` isn't being read (wrong folder, missing `ADMIN_PASSKEY` line in `settings.py`, or a hidden byte-order mark when the passkey is the first line); a trailing space inside the quotes counts as part of the passkey. Restart the server after editing `.env`.