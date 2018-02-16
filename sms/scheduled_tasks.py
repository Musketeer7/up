from django.conf import settings

from sms import sms
from sms.backends import AFEBackend
#from congenial.utils.decorator import log, LogMode


def run(minute, hour, day_of_month, month, day_of_week):
    if minute % 10 == 3:
        check_delivery_state_for_afe()
    if minute % settings.SMS_RETRY_MINUTES == 0:
        retry_sending_messages()


@log(mode=LogMode.TIME)
def check_delivery_state_for_afe():
    afe = AFEBackend()
    afe.check_delivery_state()


@log(mode=LogMode.TIME)
def retry_sending_messages():
    sms.backend.retry_sending_messages()
