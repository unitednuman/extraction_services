from django.core.management.base import BaseCommand, CommandError
import json
import re
from scrappers import scrapper_runner


# from directory_services import models

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--path', type=str)

    # with arguments
    # command :  python manage.py tester --path directory_services/data/filename
    # without arguments
    # command : python manage.py tester
    def handle(self, *args, **options):
        scrapper_runner.run()