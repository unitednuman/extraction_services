from extraction_services.models import ErrorReport
from scrappers.traceback import get_traceback
import os
import importlib
import logging
# logging.basicConfig(level=logging.DEBUG)


def run():
    logging.info("Starting....")
    module_names = os.listdir("scrappers")
    module_names.remove("__init__.py")
    module_names.remove("scrapper_runner.py")
    module_names.remove("traceback.py")
    if "__pycache__" in module_names:
        module_names.remove("__pycache__")
    for name in module_names:
        logging.info("Running :", name)
        try:
            module = importlib.import_module(f"scrappers.{name[:-3]}")
            module.run()
        except BaseException as be:
            logging.error("error in :", name)
            ErrorReport.objects.create(file_name=name, error=str(be), trace_back=str(get_traceback()))
    logging.info("Completed!")
