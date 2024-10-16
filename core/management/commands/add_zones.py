from django.core.management import BaseCommand

from core.models import Area


class Command(BaseCommand):
    def handle(self, *args, **options):
        for num in range(1,4):
            Area.objects.get_or_create(number=num)
        
        print('done')

