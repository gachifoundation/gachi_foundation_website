import json
import logging
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from .data_loader import load_json

logger = logging.getLogger(__name__)

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def page(template_name, title):
    """Factory for simple content pages rendered from core/pages/<name>.html."""
    def view(request):
        return render(request, f"pages/{template_name}.html", {"page_title": title})
    return view


def index(request):
    return render(request, "pages/index.html", {"page_title": "Home"})


def contact(request):
    """Contact form. Sends the message to settings.CONTACT_EMAIL and always
    keeps a local copy in data/contact_messages.log so nothing is ever lost."""
    sent = False
    error = ""
    form = {"name": "", "email": "", "message": ""}

    if request.method == "POST":
        form["name"] = request.POST.get("name", "").strip()[:120]
        form["email"] = request.POST.get("email", "").strip()[:200]
        form["message"] = request.POST.get("message", "").strip()[:4000]
        honeypot = request.POST.get("website", "").strip()

        if honeypot:
            # Bot filled the hidden field. Pretend success, drop the message.
            sent = True
        elif not (form["name"] and form["email"] and form["message"]):
            error = "Please fill in your name, email and message."
        else:
            try:
                validate_email(form["email"])
            except ValidationError:
                error = "Please enter a valid email address."

        if not sent and not error:
            _log_contact_message(form, request)
            subject = "Gachi Foundation website enquiry from %s" % form["name"]
            body = (
                "Name: %s\n"
                "Email: %s\n"
                "Received: %s\n"
                "IP: %s\n\n"
                "Message:\n%s\n"
            ) % (
                form["name"], form["email"],
                timezone.now().strftime("%d %b %Y %H:%M"),
                _client_ip(request), form["message"],
            )
            try:
                EmailMessage(
                    subject=subject,
                    body=body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[settings.CONTACT_EMAIL],
                    reply_to=[form["email"]],
                ).send(fail_silently=False)
                sent = True
                form = {"name": "", "email": "", "message": ""}
            except Exception:
                logger.exception("Contact form email delivery failed")
                error = ("Sorry, the message could not be sent right now. "
                         "Please email us directly at %s" % settings.CONTACT_EMAIL)

    return render(request, "pages/contactus.html",
                  {"page_title": "Contact Us", "sent": sent,
                   "error": error, "form": form})


def _client_ip(request):
    fwd = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def _log_contact_message(form, request):
    """Append every submission to data/contact_messages.log as a backup."""
    try:
        log_path = Path(settings.BASE_DIR) / "data" / "contact_messages.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write("---- %s | %s ----\n" % (
                timezone.now().strftime("%Y-%m-%d %H:%M:%S"), _client_ip(request)))
            fh.write("Name: %s\nEmail: %s\n%s\n\n" % (
                form["name"], form["email"], form["message"]))
    except Exception:
        logger.exception("Could not write contact message backup")


def team(request):
    members = load_json("team.json", [])
    return render(request, "pages/team.html",
                  {"page_title": "Our Team", "members": members})


def faq(request):
    faqs = load_json("faq.json", [])
    return render(request, "pages/faq.html",
                  {"page_title": "FAQ", "faqs": faqs})


def allngo(request):
    ngos = load_json("allngo.json", [])
    ngos = sorted(ngos, key=lambda x: x.get("name", "").lower())
    return render(request, "pages/allngo.html",
                  {"page_title": "All NGOs in India", "ngos": ngos})


def gallery(request):
    """Scan the gallery dir; filename = caption, descriptions from JSON."""
    gallery_dir = Path(settings.GALLERY_DIR)
    descriptions = {}
    desc_file = gallery_dir / "image_description.json"
    if desc_file.exists():
        try:
            descriptions = json.loads(desc_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            descriptions = {}

    images = []
    if gallery_dir.exists():
        for f in sorted(gallery_dir.iterdir()):
            if f.suffix.lower() in IMAGE_EXTS:
                caption = f.stem.replace("_", " ").replace("-", " ").title()
                images.append({
                    "url": f"{settings.STATIC_URL}gallery/{f.name}",
                    "caption": caption,
                    "description": descriptions.get(f.name, ""),
                })
    return render(request, "pages/gallery.html",
                  {"page_title": "Gallery", "images": images})


def fundwright_pricing(request):
    """Fundwright pricing page. All content is editable in data/fundwright_plans.json."""
    fw = load_json("fundwright_plans.json", {})
    seo = fw.get("seo", {})

    # Flat, de-duplicated feature list for the schema.org featureList property.
    features = []
    for plan in fw.get("plans", []):
        for f in plan.get("features", []):
            if f not in features:
                features.append(f)

    return render(request, "pages/fundwright-pricing.html", {
        "page_title": seo.get("title") or "Fundwright Pricing",
        "fw": fw,
        "fw_features": features,
    })

def sitemap(request):
    from django.urls import reverse
    names = ["index", "aboutus", "contactus", "team", "gallery", "faq",
             "privacy", "donate", "goal", "progress", "projects",
             "bankdetails", "calender", "partners", "allngo", "joinus",
             "blog", "terms", "donationpolicy", "socialmedia", "ourdocument",
             "donarlist", "links", "onlineuser", "address",
             "fundwright_pricing"]
    base = request.build_absolute_uri("/").rstrip("/")
    urls = "".join(
        f"<url><loc>{base}{reverse(n)}</loc></url>" for n in names
    )
    xml = (f'<?xml version="1.0" encoding="UTF-8"?>'
           f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
           f'{urls}</urlset>')
    return HttpResponse(xml, content_type="application/xml")


def robots(request):
    base = request.build_absolute_uri("/").rstrip("/")
    body = f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n"
    return HttpResponse(body, content_type="text/plain")


def blog(request):
    posts = load_json("blog.json", [])
    posts = sorted(posts, key=lambda p: p.get("date", ""), reverse=True)
    return render(request, "pages/blog.html",
                  {"page_title": "Blog & News", "posts": posts})


def blog_detail(request, slug):
    posts = load_json("blog.json", [])
    post = next((p for p in posts if p.get("slug") == slug), None)
    if not post:
        return render(request, "404.html", {"page_title": "Not found"}, status=404)
    return render(request, "pages/blogdetail.html",
                  {"page_title": post["title"], "post": post})


def page_not_found(request, exception=None):
    """Custom 404 (wired via handler404 in urls)."""
    return render(request, "404.html", {"page_title": "Page not found"}, status=404)
