from django.contrib.auth.management.commands.createsuperuser import Command as BaseCommand
from django.core.management import CommandError
from users.models import CustomUser


class Command(BaseCommand):

    def handle(self, *args, **options):
        email = input('Email: ')
        password = input('Password: ')
        first_name = input('First name: ')
        last_name = input('Last name: ')

        try:
            user = CustomUser.objects.create_superuser(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role='admin'
            )
            self.stdout.write(
                self.style.SUCCESS(f'Админ {email} успешно создан!')
            )
        except Exception as e:
            raise CommandError(f'Ошибка создания админа: {e}')