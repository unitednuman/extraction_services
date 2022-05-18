import uuid
from django.utils import timezone
from django.conf import settings
from django_request_context import request


def get_file_type(instance, filename):
    if hasattr(instance, 'media_type'):
        file_type = instance.media_type
    else:
        file_type = 'image'
    return file_type


def upload_user_media(instance, filename):
    data = {
        'file_type': get_file_type(instance, filename),
        'file_name': '%s.png' % str(uuid.uuid4()),
        'timestamp': timezone.now().strftime('%Y%m%d%H%M%S')
    }
    return settings.MEDIA_FILE_PATH.format(**data)


def get_file_path(file):
    if 'static' in str(file):
        return request.build_absolute_uri(str(file))
    else:
        return request.build_absolute_uri(file.url)
