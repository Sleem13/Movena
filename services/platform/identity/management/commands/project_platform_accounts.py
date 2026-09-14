from django.core.management.base import BaseCommand, CommandError
from identity.models import Account
from identity.projection import project


class Command(BaseCommand):
    help = 'Project platform-owned accounts into the legacy care reader.'

    def handle(self, *args, **options):
        count = 0
        try:
            for account in Account.objects.filter(credential_owner='platform').order_by('user_id').iterator():
                project(account)
                count += 1
        except Exception as exc:
            raise CommandError('Account projection stopped before completion.') from exc
        self.stdout.write(self.style.SUCCESS(f'Projected {count} platform-owned account(s).'))
