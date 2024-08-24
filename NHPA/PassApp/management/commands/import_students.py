from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
import csv

class Command(BaseCommand):
    help = 'Imports students from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file containing student data')

    def handle(self, *args, **options):
        # Ensure the Student group exists; create if not
        group, _ = Group.objects.get_or_create(name='student')

        with open(options['csv_file'], newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Split the full name into first and last name
                last_name, first_name = row['StudentFullName'].split(', ')
                # Create the user or get existing one
                user, created = User.objects.get_or_create(
                    username=row['StudentNumber'],
                    defaults={
                        'first_name': first_name,
                        'last_name': last_name
                    }
                )
                if created:
                    user.set_unusable_password()  # This makes the password unusable
                    user.groups.add(group)  # Add user to the Student group
                    user.save()  # Save the user after setting the password and group
                    self.stdout.write(self.style.SUCCESS(f"Successfully created user {user.username} with no usable password and added to Student group"))
                else:
                    self.stdout.write(self.style.WARNING(f"User {user.username} already exists"))