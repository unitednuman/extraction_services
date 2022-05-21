from extraction_services.models import ErrorReport
import io
import traceback
import os
import importlib


def get_traceback():
    """Get traceback of current exception"""
    sio = io.StringIO()
    traceback.print_exc(file=sio)
    return sio.getvalue()


def run():
    # base dir necesseory
    # print("here")
    module_names = os.listdir("scrappers")
    module_names.remove("__init__.py")
    module_names.remove("scrapper_runner.py")
    if "__pycache__" in module_names:
        module_names.remove("__pycache__")
    for name in module_names:
        try:
            module = importlib.import_module(f"scrappers.{name[:-3]}")
            module.run()
        except BaseException as be:
            print(be)
            ErrorReport.objects.create(file_name=name, error=str(be), path=str(get_traceback()))
