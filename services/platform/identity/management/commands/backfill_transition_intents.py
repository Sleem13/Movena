import json
from django.core.management.base import BaseCommand
from identity.backfill import transition_intents


class Command(BaseCommand):
    help = 'Report missing transition intents; use --persist to add only missing rows.'

    def add_arguments(self, parser):
        parser.add_argument('--persist', action='store_true')

    def handle(self, *args, **options):
        self.stdout.write(json.dumps(transition_intents(persist=options['persist']), indent=2))
