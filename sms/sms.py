from importlib import import_module

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from sms.backends import ADPBackend, ISMSBackend

try:
    backend_path = settings.SMS_BACKEND
    module_name, class_name = backend_path.rsplit('.', 1)
    module = import_module(module_name)
    klass = getattr(module, class_name)
    backend = klass()
except (AttributeError, ImportError):
    backend = None


def send_message(recipient, text, job=None, description="", force=False):
    """
    recipient: a number (string)
    """
    send_messages([recipient, ], text, job, description, force)


def send_messages(recipients, text, job=None, description="", force=False):
    """
    recipients: a list of numbers (list)
    """
    if not backend:
        raise ImproperlyConfigured('No backend has been specified: Settings.SMS_BACKEND')
    prefix = '98'
    recipients = [prefix + s for s in recipients]
    backend.enqueue_messages(recipients, text, job, description, force)


def get_balance():
    if backend and hasattr(backend, 'get_send_balance'):

        balance = backend.get_send_balance()
        if isinstance(backend, ADPBackend) or isinstance(backend, ISMSBackend):
            return balance.balance
    return 0
