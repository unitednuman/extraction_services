import importlib

from cffi.setuptools_ext import execfile
from django.core.management.base import BaseCommand, CommandError
import json
import re

from scrappers import scrapper_runner
from scrappers import *

# from directory_services import models

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--path', type=str)

    # with arguments
    # command :  python manage.py scrapper_tester --path allsop.py
    # without arguments
    # command : python manage.py all_scrapper_tester
    def handle(self, *args, **options):
        file_name = options['path'][:-3]
        module = importlib.import_module(f"scrappers.{file_name}")
        module.run()
