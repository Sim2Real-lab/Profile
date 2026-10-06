from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static

from django.views.generic import RedirectView

urlpatterns = [
    # Redirect double/duplicate proforma prefixes if accessed directly from old links/cache
    re_path(r'^proforma/proforma/(?P<path>.*)$', RedirectView.as_view(url='/proforma/%(path)s', permanent=False)),

    path('proforma/admin/', admin.site.urls),
    path('proforma/', include('members.urls')),
    path('', RedirectView.as_view(url='/proforma/', permanent=False)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
