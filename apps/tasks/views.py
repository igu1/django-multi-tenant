from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Task, TaskStatus, TaskPriority
from .serializers import TaskSerializer, TaskStatusSerializer, TaskPrioritySerializer


class TaskStatusViewSet(viewsets.ModelViewSet):
    serializer_class = TaskStatusSerializer
    permission_classes = []
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["order", "name", "created_at"]
    ordering = ["order", "name"]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return TaskStatus.objects.all()
        return TaskStatus.objects.filter(tenant=self.request.tenant)


class TaskPriorityViewSet(viewsets.ModelViewSet):
    serializer_class = TaskPrioritySerializer
    permission_classes = []
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["order", "name", "created_at"]
    ordering = ["order", "name"]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return TaskPriority.objects.all()
        return TaskPriority.objects.filter(tenant=self.request.tenant)


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = []
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "priority", "assigned_to", "created_by"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "due_date", "priority", "status"]
    ordering = ["-created_at"]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Task.objects.all()
        return Task.objects.filter(tenant=self.request.tenant)

    def perform_create(self, serializer):
        if not self.request.user.is_superuser:
            serializer.save(
                tenant=self.request.tenant,
                created_by=self.request.user
            )
        else:
            serializer.save(
                created_by=self.request.user,
                tenant=serializer.validated_data.get('tenant')
            )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context
