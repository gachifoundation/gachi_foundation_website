import json
from pathlib import Path

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render

from .data_loader import load_json

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def page(template_name, title):
    """Factory for simple content pages rendered from core/pages/<name>.html."""
    def view(request):
        return render(request, f"pages/{template_name}.html", {"page_title": title})
    return view


def index(request):
    return render(request, "pages/index.html", {"page_title": "Home"})


def contact(request):
    sent = False
    if request.method == "POST":
        # CSRF-protected by Django middleware. In production, wire to email/DB.
        sent = True
    return render(request, "pages/contactus.html",
                  {"page_title": "Contact Us", "sent": sent})


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


def sitemap(request):
    from django.urls import reverse
    names = ["index", "aboutus", "contactus", "team", "gallery", "faq",
             "privacy", "donate", "goal", "progress", "projects",
             "bankdetails", "calender", "partners", "allngo", "joinus",
             "blog", "terms", "donationpolicy", "socialmedia", "ourdocument",
             "donarlist", "links", "onlineuser", "address"]
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
