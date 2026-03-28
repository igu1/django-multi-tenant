from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.tenants.models import Tenant, Domain


class Command(BaseCommand):
    help = 'Create a new HRMS tenant with domain and superuser'

    def add_arguments(self, parser):
        parser.add_argument('--schema_name', type=str, required=True)
        parser.add_argument('--name', type=str, required=True)
        parser.add_argument('--domain_name', type=str, required=True)
        parser.add_argument('--email', type=str, required=True)
        parser.add_argument('--password', type=str, required=True)
        parser.add_argument('--username', type=str, default='')

    def handle(self, *args, **options):
        schema_name = options['schema_name']
        name = options['name']
        domain = options['domain_name']
        email = options['email']
        password = options['password']
        username = options['username'] or email.split('@')[0]

        # Create tenant
        tenant = Tenant.objects.create(
            schema_name=schema_name,
            name=name
        )

        # Create domain
        domain_obj = Domain()
        domain_obj.domain = domain
        domain_obj.tenant = tenant
        domain_obj.is_primary = True
        domain_obj.save()

        # Create shared superuser
        User = get_user_model()
        User.objects.create_superuser(
            email=email,
            username=username,
            password=password
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created tenant "{name}" with domain "{domain}"'
            )
        )
