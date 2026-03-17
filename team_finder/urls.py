from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


def root_redirect(request):
    return redirect("projects:list")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", root_redirect),
    path("users/", include("users.urls")),
    path("projects/", include("projects.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
