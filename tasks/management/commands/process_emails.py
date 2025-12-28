from django.core.management.base import BaseCommand
from tasks.email_utils import process_email_queue

class Command(BaseCommand):
    help = 'Process pending emails in queue'

    def handle(self, *args, **options):
        process_email_queue()
        self.stdout.write('Email queue processed')