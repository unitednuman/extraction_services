from extraction_services.models import ErrorReport
from scrappers.traceback import get_traceback
import os
import importlib




def run():
    print("Starting....")
    module_names = os.listdir("scrappers")
    module_names.remove("__init__.py")
    module_names.remove("scrapper_runner.py")
    module_names.remove("traceback.py")
    if "__pycache__" in module_names:
        module_names.remove("__pycache__")
    for name in module_names:
        try:
            module = importlib.import_module(f"scrappers.{name[:-3]}")
            module.run()
        except BaseException as be:
            report = {
                "file_name": name,
                "error": str(be),
                "path": str(get_traceback())
            }
            ErrorReport.objects.create(**report)
    print("Completed!")
