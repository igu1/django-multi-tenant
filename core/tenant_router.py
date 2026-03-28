"""
Tenant-specific URL routing for HRMS Multi-Tenant System.
These URLs are only accessible within tenant contexts and are isolated per tenant.
"""

from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Tenant-specific application URLs
# Each tenant gets their own isolated versions of these apps
tenant_app_patterns = [
    path('api/tasks/', include('apps.tasks.urls')),
    path('api/leave/', include('apps.leave.urls')),
    path('api/dashboard/', include('apps.dashboard.urls')),
]

tenant_public_patterns = [
    # Add tenant-specific public URLs here
    # path('login/', include('apps.tenants.urls')),
]

urlpatterns = tenant_app_patterns + tenant_public_patterns
