from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from analyzer.models import UserProfile


class Command(BaseCommand):
    help = 'Create UserProfile for all users who dont have one'

    def handle(self, *args, **options):
        users_without_profile = User.objects.filter(profile__isnull=True)
        
        if not users_without_profile.exists():
            self.stdout.write(self.style.SUCCESS('All users already have profiles'))
            return
        
        count = 0
        for user in users_without_profile:
            UserProfile.objects.create(user=user)
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Created {count} user profiles'))
