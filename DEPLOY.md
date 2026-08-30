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
   `www.gachifoundation.org`. Render gives you a CNAME target - add it in GoDaddy.
   SSL is automatic.

### Contact form email on Render

`.env` is never committed, so the Gmail app password must be set in the Render
dashboard: **your service → Environment → Add Environment Variable**.

| Key | Value |
|---|---|
| `EMAIL_HOST` | `smtp.gmail.com` |
| `EMAIL_PORT` | `587` |
| `EMAIL_USE_TLS` | `True` |
| `EMAIL_HOST_USER` | `gachifoundation@gmail.com` |
| `EMAIL_HOST_PASSWORD` | the 16-character Gmail app password |
| `DEFAULT_FROM_EMAIL` | `gachifoundation@gmail.com` |
| `CONTACT_EMAIL` | `gachifoundation@gmail.com` |

Click **Save Changes**. Render redeploys automatically. All of these except the
password are already listed in `render.yaml`, so a Blueprint deploy only prompts
you for `EMAIL_HOST_PASSWORD`.

**Important limitation:** since September 2025 Render blocks outbound SMTP ports
25, 465 and 587 on **free** web services. On the free plan the contact form page
will still work and every message is still saved to `data/contact_messages.log`,
but no email will arrive. To get email delivery you must either upgrade the
service to a paid instance type (Starter, $7/mo) or switch the contact form to an
email API that sends over HTTPS instead of SMTP, such as Brevo, Resend or SendGrid.
This limit is specific to Render. PythonAnywhere (Option A) allows SMTP to Gmail
on its paid plans without this restriction.

To verify after deploying, open the service **Shell** tab and run:

```bash
python manage.py shell -c "from django.core.mail import send_mail; from django.conf import settings; send_mail('Render test','It works.',settings.DEFAULT_FROM_EMAIL,[settings.CONTACT_EMAIL]); print('sent')"
```

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
