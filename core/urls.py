# core/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.pages import views

urlpatterns = [
    # ✅ PRIMERO EL ADMIN (debe ir antes del catch-all)
    path('admin/', admin.site.urls),
    
    # ✅ TUS URLs DE LA APP
    path('', include('apps.pages.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)