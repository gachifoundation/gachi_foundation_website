# Deploying Gachi Foundation (domain at GoDaddy, app hosted elsewhere)

You keep the **domain registered at GoDaddy** and host the Django app on a cheap,
Django-friendly platform. Two recommended options below — pick one.

WhiteNoise is already configured, so the app serves its own CSS/JS/images. You do
**not** need a separate static-file server.

---

## OPTION A — PythonAnywhere  (recommended: ~$5/mo, always on, simplest)

1. Create an account at https://www.pythonanywhere.com and take the **Hacker ($5/mo)**
   plan (required for a custom domain).
2. **Upload the code**: either `git clone` your repo in a Bash console, or upload
   the zip and unzip it. Aim for `/home/<user>/gachi_foundation_website`.
3. In a **Bash console**:
   ```bash
   cd ~/gachi_foundation_website
   python3 -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py collectstatic --noinput
   python manage.py createsuperuser   # optional
   ```
4. **Web tab → Add a new web app → Manual configuration → Python 3.12.**
   - **Source code:** `/home/<user>/gachi_foundation_website`
   - **Virtualenv:** `/home/<user>/gachi_foundation_website/venv`
   - **WSGI file:** edit it to point at Django:
     ```python
     import os, sys
     path = "/home/<user>/gachi_foundation_website"
     if path not in sys.path: sys.path.append(path)
     os.environ["DJANGO_SETTINGS_MODULE"] = "gachi.settings"
     os.environ["DJANGO_DEBUG"] = "False"
     os.environ["DJANGO_SECRET_KEY"] = "<paste a long random string>"
     os.environ["DJANGO_ALLOWED_HOSTS"] = "<user>.pythonanywhere.com,gachifoundation.org,www.gachifoundation.org"
     from django.core.wsgi import get_wsgi_application
     application = get_wsgi_application()
     ```
5. **Static files mapping** (Web tab → Static files):
   URL `/static/`  →  Directory `/home/<user>/gachi_foundation_website/staticfiles`
6. Click **Reload**. The site is live at `<user>.pythonanywhere.com`.
7. **Custom domain:** Web tab → enter `www.gachifoundation.org`. PythonAnywhere shows
   a **CNAME target** — add it in GoDaddy DNS (see "Point GoDaddy" below). Enable the
   free HTTPS certificate on the Web tab once DNS resolves.

---

## OPTION B — Render  (free tier available; $7/mo "Starter" to avoid idle sleep)

1. Push this project to a **GitHub** repo.
2. On https://render.com → **New + → Blueprint** → select the repo. It reads the
   included `render.yaml` and configures everything (build, migrate, collectstatic,
   gunicorn, env vars).
3. After the first deploy, set `DJANGO_ALLOWED_HOSTS` to include your real domain
   (already pre-filled with `gachifoundation.org`) and trigger a redeploy.
4. **Custom domain:** Render dashboard → Settings → Custom Domains → add
   `www.gachifoundation.org`. Render gives you a CNAME target — add it in GoDaddy.
   SSL is automatic.

(The repo also includes a `Procfile`, so Railway works the same way if you prefer it.)

---

## Point the GoDaddy domain at your host

In **GoDaddy → My Products → Domain → DNS → Manage DNS**:

- Add/edit a **CNAME** record:
  - **Name:** `www`
  - **Value:** the target your host gave you
    (e.g. `<user>.pythonanywhere.com` or `gachi-foundation.onrender.com`)
- For the root domain (`gachifoundation.org` with no `www`):
  - PythonAnywhere: use their instructions (often a redirect from root to `www`).
  - Render: add the domain in Render and use the **A record / ALIAS** values it provides,
    or set a GoDaddy **Forwarding** rule from the root to `https://www.…`.

DNS changes take from a few minutes up to a few hours to propagate. Once live,
verify HTTPS works and that `https://<domain>/sitemap.xml` and `/robots.txt` load.

---

## After any content change
Edit the JSON files in `data/` (and images in `static/`), then redeploy / reload.
If you change CSS/JS, re-run `python manage.py collectstatic --noinput` (PythonAnywhere)
or just push to GitHub (Render runs it automatically).
