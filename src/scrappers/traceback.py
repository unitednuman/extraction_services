import io
import traceback
from threading import Thread

from django.core.exceptions import SynchronousOnlyOperation

from extraction_services.models import ErrorReport


def get_traceback():
    """Get traceback of current exception"""
    sio = io.StringIO()
    traceback.print_exc(file=sio)
    return sio.getvalue()


def save_error_report(exception, filename, **kwargs):
    try:
        _save_error_report(exception, filename, **kwargs)
    except SynchronousOnlyOperation:
        t = Thread(target=_save_error_report, daemon=True, args=(exception, filename,), kwargs=kwargs)
        t.start()
        t.join()


def _save_error_report(exception, filename, **kwargs):
    _traceback = get_traceback()
    exception = str(exception)
    if error_report := ErrorReport.objects.filter(trace_back=_traceback, error=exception).first():
        error_report.count = error_report.count + 1
        error_report.__dict__.update(kwargs)
        error_report.save()
    else:
        ErrorReport.objects.create(file_name=filename, error=exception, trace_back=_traceback, **kwargs)
