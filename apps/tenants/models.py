from django.contrib.auth.models import AbstractUser, UserManager
from django.db import connection, models
from django_tenants.models import TenantMixin, DomainMixin


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True



class TenantScopedManager(UserManager):
    def get_queryset(self):
        queryset = super().get_queryset()
        current_tenant = getattr(connection, "tenant", None)
        if not current_tenant or getattr(current_tenant, "schema_name", None) == "public":
            return queryset
        return queryset.filter(tenant=current_tenant)


class TenantScopedModel(TimeStampedModel):
    tenant = models.ForeignKey(
        "Tenant",
        on_delete=models.CASCADE,
        related_name="tenant_scoped_models",
    )

    objects = TenantScopedManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True


class User(AbstractUser, TenantScopedModel):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class Tenant(TenantMixin, TimeStampedModel):
    name = models.CharField(max_length=100)


class Domain(DomainMixin, TimeStampedModel):
    pass
