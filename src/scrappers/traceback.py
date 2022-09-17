import inspect
import io
import os
import traceback
from threading import Thread
from django.core.exceptions import SynchronousOnlyOperation
from extraction_services.models import ErrorReport, LoggerModel


def get_traceback():
    """Get traceback of current exception"""
    sio = io.StringIO()
    traceback.print_exc(file=sio)
    return sio.getvalue()


def save_error_report(exception, filename=None, **kwargs):
    try:
        _save_error_report(exception, filename, **kwargs)
    except SynchronousOnlyOperation:
        t = Thread(
            target=_save_error_report,
            daemon=True,
            args=(
                exception,
                filename,
            ),
            kwargs=kwargs,
        )
        t.start()
        t.join()


def _save_error_report(exception, filename=None, **kwargs):
    _traceback = get_traceback()
    exception = str(exception)
    try:
        filenames = ", ".join({os.path.basename(s.filename) for s in inspect.stack() if r"scrappers" in s.filename})
    except Exception as e:
        if kwargs.get("secondary_error"):
            LoggerModel.debug(f"error while fetching filenames: {e}", filenames="")
        else:
            LoggerModel.info(f"error while fetching filenames: {e}", filenames="")
        filenames = ""
    # LoggerModel.error(f"Got error {exception}, {kwargs}")
    if error_report := ErrorReport.objects.filter(trace_back=_traceback, error=exception).first():
        error_report.count = error_report.count + 1
        error_report.__dict__.update(kwargs)
        error_report.save()
    else:
        ErrorReport.objects.create(file_name=filenames, error=exception, trace_back=_traceback, **kwargs)
