from django.http import JsonResponse
from django_tenants.utils import get_tenant
from django.contrib.auth import get_user_model

User = get_user_model()

def test_view(request):
    """Test view"""
    current_tenant = getattr(request, 'tenant', None)

    if hasattr(request, 'user') and request.user.is_superuser:
        users = list(User.all_objects.all().values('username', 'email'))
    else:
        users = list(User.objects.all().values('username', 'email'))
    
    return JsonResponse({
        'message': 'Test view working',
        'tenant': current_tenant.name if current_tenant else 'No tenant',
        'users': users
    })