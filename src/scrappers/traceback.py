import io
import traceback
from extraction_services.models import ErrorReport


def get_traceback():
    """Get traceback of current exception"""
    sio = io.StringIO()
    traceback.print_exc(file=sio)
    return sio.getvalue()


def save_error_report(exception):
    _traceback = get_traceback()
    exception = str(exception)
    if error_report := ErrorReport.objects.filter(trace_back=_traceback, error=exception).first():
        error_report.count = error_report.count + 1
        error_report.save()
    else:
        ErrorReport.objects.create(file_name="auctionhouse.py", error=exception, trace_back=_traceback)