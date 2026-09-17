import os
from django.core.management.base import BaseCommand, CommandError
from identity.provisioning import ProvisioningDenied
from identity.seeding import seed_protected_superadmin


class Command(BaseCommand):
    help = 'Create or explicitly reset the protected platform super-administrator.'

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true')

    def handle(self, *args, **options):
        values = [os.environ.get(name, '') for name in (
            'MOVENA_SUPER_ADMIN_EMAIL', 'MOVENA_SUPER_ADMIN_USERNAME',
            'MOVENA_SUPER_ADMIN_FULL_NAME', 'MOVENA_SUPER_ADMIN_PASSWORD')]
        if not all(values):
            raise CommandError('All MOVENA_SUPER_ADMIN_* settings are required.')
        try:
            account, changed = seed_protected_superadmin(*values, reset=options['reset'])
        except ProvisioningDenied as exc:
            raise CommandError('Protected super-administrator provisioning was denied.') from exc
        status = 'updated' if changed else 'already configured'
        self.stdout.write(self.style.SUCCESS(f'Protected super-administrator {status}: {account.user_id}'))
