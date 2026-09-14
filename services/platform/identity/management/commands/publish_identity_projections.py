from django.core.management.base import BaseCommand
from identity.projection import publish_pending


class Command(BaseCommand):
    help = 'Publish pending account projections to the legacy care reader.'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=100)

    def handle(self, *args, **options):
        result = publish_pending(limit=options['limit'])
        self.stdout.write(self.style.SUCCESS(
            f"Selected {result['selected']}; published {result['published']}; failed {result['failed']}."))
