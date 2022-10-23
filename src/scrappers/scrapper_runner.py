import sys
from subprocess import Popen, TimeoutExpired
from extraction_services.models import LoggerModel
from scrappers.traceback import save_error_report
import os
import importlib

# logging.basicConfig(level=logging.DEBUG)


def run():
    # logging.info("Starting....")
    LoggerModel.delete_previous_logs()
    LoggerModel.info("Starting....")
    module_names = os.listdir("scrappers")
    module_names.remove("__init__.py")
    module_names.remove("scrapper_runner.py")
    module_names.remove("traceback.py")
    if "__pycache__" in module_names:
        module_names.remove("__pycache__")
    for name in module_names:
        # logging.info("Running :", name)
        try:
            module = importlib.import_module(f"scrappers.{name[:-3]}")
            if hasattr(module, "run"):
                max_wait = getattr(module, "MAX_WAIT", 15 * 60)
                LoggerModel.info(f"Running: {name}")
                # module.run()
                cmd = [sys.executable, "manage.py", "scrapper_tester", "--path", name]
                process = Popen(cmd)
                try:
                    process.wait()
                except TimeoutExpired:
                    LoggerModel.info(f"Waited {max_wait} seconds for {name}, going to terminate it.")
                    process.terminate()

        except BaseException as be:
            # logging.error("error in :", name)
            LoggerModel.error(f"error in :{name}")
            save_error_report(be, name)
            # _traceback = get_traceback()
            # if error_report := ErrorReport.objects.filter(trace_back=_traceback).first():
            #     error_report.count = error_report.count + 1
            #     error_report.save()
            # else:
            #     ErrorReport.objects.create(file_name=name, error=str(be), trace_back=_traceback)
    LoggerModel.info("Completed!")
