from django.utils.deprecation import MiddlewareMixin
from django_tenants.utils import get_tenant


class TenantSwitchMiddleware(MiddlewareMixin):
    """
    Middleware to handle tenant switching based on URL or headers
    """
    
    def process_request(self, request):
        pass


class TenantContextMiddleware(MiddlewareMixin):
    """
    Middleware to add tenant context to requests
    """
    
    def process_request(self, request):
        try:
            current_tenant = get_tenant(request)
            request.current_tenant = current_tenant
        except:
            request.current_tenant = None
