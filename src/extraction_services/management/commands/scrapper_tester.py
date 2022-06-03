import importlib
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--path', type=str)

    # command :  python manage.py scrapper_tester --path allsop.py
    def handle(self, *args, **options):
        file_name = options['path'][:-3]
        module = importlib.import_module(f"scrappers.{file_name}")
        module.run()
