import io
import traceback

def get_traceback():
    """Get traceback of current exception"""
    sio = io.StringIO()
    traceback.print_exc(file=sio)
    return sio.getvalue()
