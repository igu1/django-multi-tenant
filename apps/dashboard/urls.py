from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
# Register your viewsets here when you create them

urlpatterns = [
    path('', include(router.urls)),
    path('test/', views.test_view, name='test'),
]
