from django.core.management.base import BaseCommand
from scrappers import scrapper_runner




class Command(BaseCommand):

    # command : python manage.py all_scrapper_tester
    def handle(self, *args, **options):
        scrapper_runner.run()
