import logging

from jsonrpc import jsonrpc_method

from sms.sms import send_message


logger = logging.getLogger('Notify Serrvice Connection')

@jsonrpc_method('send_sms')
def send_sms(request, recipient, text, job=None, description="", force=False):
    try:
        send_message(recipient, text, job, description, force)
    except Exception as e:
        logger.error(e)
        raise e