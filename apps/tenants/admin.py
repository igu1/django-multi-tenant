from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django_tenants.utils import schema_context
from django_tenants.admin import TenantAdminMixin
from .models import Tenant, Domain, User


class UserAdmin(BaseUserAdmin):
    list_display = ["id", "email", "tenant", "is_active", "is_superuser", "get_groups"]
    list_display_links = ["id", "email"]
    search_fields = ["email"]
    
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "email",
                    "password",
                ],
            },
        ),
        (
            "Permissions",
            {
                "fields": [
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ],
            },
        ),
        (
            "Important dates",
            {
                "fields": [
                    "last_login",
                    "date_joined",
                ],
            },
        ),
        (
            "Tenant",
            {
                "fields": [
                    "tenant",
                ],
            },
        ),
    ]

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj=obj))
        if not request.user.is_superuser:
            readonly_fields.append("tenant")
        return readonly_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "tenant" and request.user.is_superuser:
            with schema_context("public"):
                kwargs["queryset"] = Tenant.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        if request.user.is_superuser:
            return User.all_objects.get_queryset()

        queryset = super().get_queryset(request)

        current_tenant = getattr(request, "tenant", None)
        if not current_tenant or getattr(current_tenant, "schema_name", None) == "public":
            return queryset.none()

        return queryset.filter(tenant=current_tenant)

    def save_model(self, request, obj, form, change):
        if not change:
            pass
        else:
            if 'password' in form.changed_data:
                obj.set_password(obj.password)

        if obj.is_superuser:
            if obj.tenant_id is None and 'tenant' not in form.changed_data:
                obj.tenant = None
        else:
            current_tenant = getattr(request, "tenant", None)
            if current_tenant and getattr(current_tenant, "schema_name", None) != "public":
                if not request.user.is_superuser:
                    obj.tenant = current_tenant
                elif obj.tenant_id is None:
                    obj.tenant = current_tenant

        super().save_model(request, obj, form, change)

    def get_groups(self, obj):
        return ", ".join([g.name for g in obj.groups.all()])
    get_groups.short_description = "Groups"


class TenantAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ["schema_name", "name", "created_at", "updated_at"]


class DomainAdmin(admin.ModelAdmin):
    list_display = ["domain", "tenant", "is_primary", "created_at", "updated_at"]


admin.site.register(Tenant, TenantAdmin)
admin.site.register(Domain, DomainAdmin)
admin.site.register(User, UserAdmin)
