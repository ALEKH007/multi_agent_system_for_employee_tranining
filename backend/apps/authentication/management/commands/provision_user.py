from getpass import getpass

from django.core.management.base import BaseCommand, CommandError

from apps.authentication.models import User
from common.validators import validate_password_strength


class Command(BaseCommand):
    help = 'Create a privileged or employee account outside the public registration flow.'

    def add_arguments(self, parser):
        parser.add_argument('--email', required=True)
        parser.add_argument('--role', required=True, choices=User.ROLE_CHOICES)
        parser.add_argument('--employee-id')

    def handle(self, *args, **options):
        email = options['email'].lower()
        if User.objects(email=email).first():
            raise CommandError('A user with this email already exists.')

        password = getpass('Password: ')
        confirmation = getpass('Confirm password: ')
        if password != confirmation:
            raise CommandError('Passwords do not match.')
        try:
            validate_password_strength(password)
        except Exception as error:
            raise CommandError(str(error)) from error

        user = User(
            email=email,
            role=options['role'],
            employee_id=options.get('employee_id'),
        )
        user.set_password(password)
        user.save()
        self.stdout.write(self.style.SUCCESS(f'Provisioned {user.role} account for {user.email}.'))
