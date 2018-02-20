from importlib import import_module

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from sms.backends import ADPBackend, ISMSBackend

from kavenegar import *

try:
	backend_path = settings.SMS_BACKEND
	module_name, class_name = backend_path.rsplit('.', 1)
	module = import_module(module_name)
	klass = getattr(module, class_name)
	backend = klass()
except (AttributeError, ImportError):
	backend = None


def send_message(recipient, passcode, job=None, description="", force=False):
	"""
	recipient: a number (string)
	"""
	# send_messages(recipient, text, job, description, force)

	api = KavenegarAPI('6951385871546338356E7A45742B38744A397A6561343666354D2B4A4F5A6871')
	number = "0"+recipient
	text = "Your activation code is: "+passcode
	params = {
	'sender': '100065995',
	'receptor': number,
	'message' : text
	}
	response = api.sms_send(params)


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
