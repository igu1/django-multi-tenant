from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from apps.tenants.models import Tenant, Domain


class Command(BaseCommand):
    help = 'Remove a tenant and its domain'

    def add_arguments(self, parser):
        parser.add_argument('--schema_name', type=str, required=True)
        parser.add_argument('--force', action='store_true', 
                          help='Force removal without confirmation')

    def handle(self, *args, **options):
        schema_name = options['schema_name']
        force = options['force']

        try:
            tenant = Tenant.objects.get(schema_name=schema_name)
        except Tenant.DoesNotExist:
            raise CommandError(f'Tenant "{schema_name}" does not exist')

        if not force:
            confirm = input(f'Are you sure you want to delete tenant "{tenant.name}" '
                          f'(schema: {schema_name})? (y/N): ')
            if confirm.lower() != 'y':
                self.stdout.write(self.style.WARNING('Operation cancelled'))
                return

        # Get all domains for this tenant
        domains = Domain.objects.filter(tenant=tenant)
        domain_count = domains.count()

        # Switch to tenant schema to drop it
        connection.set_schema_to_public()
        connection.set_tenant(tenant)

        # Drop tenant schema
        with connection.cursor() as cursor:
            cursor.execute(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE;')

        # Switch back to public
        connection.set_schema_to_public()

        # Delete domains and tenant
        domains.delete()
        tenant.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully removed tenant "{tenant.name}" '
                f'and {domain_count} domain(s)'
            )
        )
