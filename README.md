# Gachi Foundation — Website (Django)

Award-grade, mobile-responsive NGO website for **Gachi Foundation** (a Section 8
non-profit, Jharkhand, India). Live caustic-water background, drifting mahua
flowers, Instrument Serif typography, sticky header, full-bleed animated footer,
JSON-driven content and security hardening.

---

## 1. Run locally (PyCharm or terminal)

```bash
# from the project root (the folder containing manage.py)

python -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate            # creates db.sqlite3
python manage.py createsuperuser    # optional, for /admin
python manage.py runserver
```

Open **http://127.0.0.1:8000**

In PyCharm: open this folder, set the venv as the project interpreter, then add a
*Django Server* run configuration (or just run `manage.py runserver`).

---

## 2. Deploy to a server (production)

```bash
# 1. create a .env file next to manage.py (see .env.example) and set:
#    DJANGO_DEBUG=False
#    DJANGO_SECRET_KEY=<a long random string>
#    DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

pip install -r requirements.txt
pip install gunicorn               # production WSGI server

python manage.py migrate
python manage.py collectstatic --noinput   # gathers static files into /staticfiles

gunicorn gachi.wsgi:application --bind 0.0.0.0:8000
```

Put Nginx/Apache in front to serve `/static/` (from `staticfiles/`) and `/media/`,
and to terminate HTTPS. With `DJANGO_DEBUG=False` the project automatically enables
HSTS, SSL redirect and secure cookies.

---

## 3. Editing content (no code required)

| What to change | File |
|---|---|
| Name, tagline, address, bank, social links, **last-updated date**, tawk.to chat | `data/ngo.json` |
| Team members (name, position, qualification, photo) | `data/team.json` |
| FAQ | `data/faq.json` |
| NGO directory (All NGOs page) | `data/allngo.json` |
| Blog / News posts | `data/blog.json` |
| Gallery photos | drop image files into `static/gallery/` (filename = caption) |
| Gallery captions/descriptions | `static/gallery/image_description.json` |
| Logo | replace `static/img/logo.png` |
| Donation QR | replace `static/img/qr-bank.jpg` |

Edits to the JSON files appear across the whole site immediately on refresh.

---

## 4. Adding a new page

1. Create `templates/pages/<name>.html` that starts with `{% extends "base.html" %}`
   and puts content inside `{% block content %}…{% endblock %}`.
2. Add a route in `gachi/urls.py`:
   `path("<url>/", views.page("<name>", "Page Title"), name="<name>")`
   (use a dedicated view function instead if the page needs data).
3. Header, footer, background, mobile menu, SEO and the "last updated" stamp are
   inherited automatically. Reuse the CSS classes documented at the top of
   `static/css/style.css` (`.section`, `.container`, `.card`, `.grid`, `.btn`, …).

---

## 5. Project structure

```
gachi/            Django project (settings, urls, wsgi)
core/             app: views, JSON data loader, context processor
data/             editable JSON content (ngo, team, faq, blog, allngo)
templates/        base.html, 404.html, pages/*.html
static/css/       style.css  (fully commented design system)
static/js/        main.js (behaviour), flowers.js (mahua sprites)
static/img/       logo.png, qr-bank.jpg, …
static/gallery/   gallery images + image_description.json
```

## 6. SEO & security (already built in)

- `sitemap.xml` and `robots.txt` are generated dynamically.
- Schema.org `NGO` JSON-LD, Open Graph and Twitter meta in `base.html`.
- Custom 404 page.
- Hardened settings: CSRF, XSS, clickjacking, secure cookies, and auto-HSTS/SSL
  when `DJANGO_DEBUG=False`.

## 7. Notes

- The water/footer animation uses three.js (loaded from CDN) and gracefully does
  nothing if unavailable; mahua flowers respect "reduce motion" settings.
- The drifting flowers are vector (SVG) sprites in `static/js/flowers.js`. To use a
  real photo, replace that array with `['/static/img/your-flower.png']`.
