from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from seqr.utils.communication_utils import send_reset_password_email


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-e', '--email-address', required=True, help="Email address of an existing user in the DB.")

    def handle(self, *args, **options):
        user = User.objects.get(email__iexact=options['email_address'])
        send_reset_password_email(user)
