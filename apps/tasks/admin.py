from django.contrib import admin
from .models import Task, TaskStatus, TaskPriority


@admin.register(TaskStatus)
class TaskStatusAdmin(admin.ModelAdmin):
    list_display = ["name", "order", "created_at"]
    list_editable = ["order"]
    search_fields = ["name"]


@admin.register(TaskPriority)
class TaskPriorityAdmin(admin.ModelAdmin):
    list_display = ["name", "order", "created_at"]
    list_editable = ["order"]
    search_fields = ["name"]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["title", "status", "priority", "assigned_to", "due_date", "created_at"]
    list_filter = ["status", "priority", "created_at"]
    search_fields = ["title", "description"]
    list_editable = ["status", "priority", "assigned_to"]
    autocomplete_fields = ["assigned_to", "created_by"]
    
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "title",
                    "description",
                ],
            },
        ),
        (
            "Assignment",
            {
                "fields": [
                    "assigned_to",
                    "created_by",
                ],
            },
        ),
        (
            "Details",
            {
                "fields": [
                    "status",
                    "priority",
                    "due_date",
                    "completed_at",
                ],
            },
        ),
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(tenant=request.tenant)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ["assigned_to", "created_by"]:
            if not request.user.is_superuser and hasattr(request, "tenant"):
                kwargs["queryset"] = kwargs["queryset"].filter(tenant=request.tenant)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
