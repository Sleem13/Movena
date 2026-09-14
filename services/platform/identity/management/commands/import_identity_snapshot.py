import json
from django.core.management.base import BaseCommand, CommandError
from identity.importer import import_snapshot, SnapshotError


class Command(BaseCommand):
    help = 'Verify a legacy SQLite identity copy; rolls back unless --persist is supplied.'

    def add_arguments(self, parser):
        parser.add_argument('source')
        parser.add_argument('--persist', action='store_true')

    def handle(self, *args, **options):
        try:
            self.stdout.write(json.dumps(import_snapshot(options['source'], persist=options['persist']), indent=2))
        except SnapshotError as exc:
            raise CommandError(str(exc)) from None
