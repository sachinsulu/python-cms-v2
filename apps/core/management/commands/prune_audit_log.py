from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.core.models import AuditLog


class Command(BaseCommand):
    help = 'Delete audit log entries older than N days (default: 90)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Delete entries older than this many days',
        )

    def handle(self, *args, **options):
        days      = options['days']
        cutoff    = timezone.now() - timedelta(days=days)
        deleted, _ = AuditLog.objects.filter(timestamp__lt=cutoff).delete()
        self.stdout.write(
            self.style.SUCCESS(f'Deleted {deleted} audit log entries older than {days} days.')
        )
