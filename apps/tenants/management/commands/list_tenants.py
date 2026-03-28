from django.core.management.base import BaseCommand
from apps.tenants.models import Tenant, Domain


class Command(BaseCommand):
    help = 'List all tenants and their domains'

    def handle(self, *args, **options):
        tenants = Tenant.objects.all().order_by('name')
        
        if not tenants:
            self.stdout.write(self.style.WARNING('No tenants found'))
            return

        self.stdout.write(self.style.SUCCESS('Available tenants:'))
        self.stdout.write('=' * 50)
        
        for tenant in tenants:
            domains = Domain.objects.filter(tenant=tenant)
            domain_list = ', '.join([d.domain for d in domains])
            
            self.stdout.write(f'Name: {tenant.name}')
            self.stdout.write(f'Schema: {tenant.schema_name}')
            self.stdout.write(f'Domain(s): {domain_list}')
            self.stdout.write(f'Created: {tenant.created_at.strftime("%Y-%m-%d %H:%M")}')
            self.stdout.write('-' * 30)
