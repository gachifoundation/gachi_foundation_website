from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from core import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index, name="index"),
    path("about/", views.page("aboutus", "About Us"), name="aboutus"),
    path("contact/", views.contact, name="contactus"),
    path("team/", views.team, name="team"),
    path("gallery/", views.gallery, name="gallery"),
    path("faq/", views.faq, name="faq"),
    path("address/", views.page("address", "Address"), name="address"),
    path("privacy/", views.page("privacy", "Privacy Policy"), name="privacy"),
    path("donate/", views.page("donate", "Donate"), name="donate"),
    path("goals/", views.page("goal", "Our Goals"), name="goal"),
    path("progress/", views.page("progress", "Progress"), name="progress"),
    path("documents/", views.page("ourdocument", "Our Documents"), name="ourdocument"),
    path("links/", views.page("links", "Useful Links"), name="links"),
    path("donors/", views.page("donarlist", "Donor List"), name="donarlist"),
    path("projects/", views.page("projects", "Projects"), name="projects"),
    path("bank-details/", views.page("bankdetails", "Bank Details"), name="bankdetails"),
    path("social/", views.page("socialmedia", "Social Media"), name="socialmedia"),
    path("calendar/", views.page("calender", "Calendar"), name="calender"),
    path("partners/", views.page("partners", "Partners"), name="partners"),
    path("online-users/", views.page("onlineuser", "Online Users"), name="onlineuser"),
    path("all-ngos/", views.allngo, name="allngo"),
    path("join/", views.page("joinus", "Join Us"), name="joinus"),
    path("blog/", views.blog, name="blog"),
    path("blog/<slug:slug>/", views.blog_detail, name="blog_detail"),
    path("terms/", views.page("terms", "Terms of Use"), name="terms"),
    path("donation-policy/", views.page("donationpolicy", "Donation & Refund Policy"), name="donationpolicy"),
    path("bank/", views.page("bankdetails", "Bank Details"), name="bank"),
    path("social-media/", views.page("socialmedia", "Social Media"), name="social"),
    path("sitemap.xml", views.sitemap, name="sitemap"),
    path("robots.txt", views.robots, name="robots"),
]

handler404 = "core.views.page_not_found"

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / "static")
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
