import json
import os
from django.core.management.base import BaseCommand, CommandError
from identity.importer import SnapshotError
from identity.ownership import transfer_snapshot


class Command(BaseCommand):
    help = 'Verify an exact source snapshot; --execute requires environment confirmation.'
    def add_arguments(self, parser):
        parser.add_argument('source')
        parser.add_argument('--execute', action='store_true')
    def handle(self, *args, **options):
        try:
            result=transfer_snapshot(options['source'], execute=options['execute'],
                confirmation=os.environ.get('MOVENA_IDENTITY_TRANSFER_CONFIRMATION'))
        except SnapshotError as exc:
            raise CommandError(str(exc)) from None
        self.stdout.write(json.dumps(result, indent=2))
