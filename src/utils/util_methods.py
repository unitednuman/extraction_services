from django_request_context import request
from django.conf import settings
from django.core import signing


class UtilMethods:

    @staticmethod
    def get_api_details():
        detail = {
            'service': request.version.split('-')[1],
            'version': int(request.version.split('-')[0].replace('v', ''))
        }
        return detail

    @staticmethod
    def encrypt(message):
        encrypted = signing.dumps(message)
        return encrypted

    @staticmethod
    def decrypt(message):
        decrypted = signing.loads(message)
        return decrypted
