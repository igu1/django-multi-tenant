from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'tasks', views.TaskViewSet)
router.register(r'statuses', views.TaskStatusViewSet, basename='taskstatus')
router.register(r'priorities', views.TaskPriorityViewSet, basename='taskpriority')

urlpatterns = [
    path('', include(router.urls)),
]
