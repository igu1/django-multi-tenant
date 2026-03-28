from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'tenants'

# Tenant-specific URLs
tenant_urlpatterns = [
    path('tasks/', include('apps.tasks.urls')),
    path('leave/', include('apps.leave.urls')),
    path('dashboard/', include('apps.dashboard.urls')),

]

# Public URLs (shared across all tenants)
public_urlpatterns = [
    path('tenant-info/', views.tenant_info, name='tenant_info'),
]

urlpatterns = tenant_urlpatterns + public_urlpatterns

# Static files serving
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
