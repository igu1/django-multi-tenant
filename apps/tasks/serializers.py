from rest_framework import serializers
from .models import Task, TaskStatus, TaskPriority
from django.contrib.auth import get_user_model

User = get_user_model()


class TaskStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskStatus
        fields = ["id", "name", "order", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class TaskPrioritySerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskPriority
        fields = ["id", "name", "order", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class TaskSerializer(serializers.ModelSerializer):
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        allow_null=True,
        required=False
    )
    created_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        allow_null=True,
        required=False
    )
    status = serializers.PrimaryKeyRelatedField(
        queryset=TaskStatus.objects.all(),
        allow_null=True,
        required=False
    )
    priority = serializers.PrimaryKeyRelatedField(
        queryset=TaskPriority.objects.all(),
        allow_null=True,
        required=False
    )

    class Meta:
        model = Task
        fields = [
            "id", "title", "description", "due_date", "status", "priority",
            "assigned_to", "created_by", "completed_at", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at", "created_by"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and not request.user.is_superuser and hasattr(request, "tenant"):
            self.fields["assigned_to"].queryset = User.objects.filter(tenant=request.tenant)
            self.fields["created_by"].queryset = User.objects.filter(tenant=request.tenant)
            self.fields["status"].queryset = TaskStatus.objects.filter(tenant=request.tenant)
            self.fields["priority"].queryset = TaskPriority.objects.filter(tenant=request.tenant)

    def validate_assigned_to(self, value):
        request = self.context.get("request")
        if value and request and not request.user.is_superuser:
            if value.tenant != request.tenant:
                raise serializers.ValidationError("Cannot assign user from a different tenant.")
        return value

    def validate_status(self, value):
        request = self.context.get("request")
        if value and request and not request.user.is_superuser:
            if value.tenant != request.tenant:
                raise serializers.ValidationError("Invalid status for this tenant.")
        return value

    def validate_priority(self, value):
        request = self.context.get("request")
        if value and request and not request.user.is_superuser:
            if value.tenant != request.tenant:
                raise serializers.ValidationError("Invalid priority for this tenant.")
        return value
