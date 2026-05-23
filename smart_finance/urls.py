"""
URL configuration for smart_finance project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Root URL redirects to dashboard (which handles login_required redirect)
    path('', RedirectView.as_view(pattern_name='dashboard', permanent=False)),
    
    # App URLs
    path('', include('authentication.urls')),
    path('', include('expenses.urls')),
    path('', include('ai_assistant.urls')),
    path('', include('notifications.urls')),
    path('', include('reports.urls')),
]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
