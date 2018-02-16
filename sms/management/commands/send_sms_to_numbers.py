from django.core.management.base import BaseCommand

from congenial.sms.sms import send_messages


class Command(BaseCommand):
    help = 'This command sends sms to users in a file as argument' \
        '(First line is the message, second line is the description of the messages, each line of file is the number of a user).'
    args = '<file_name> <job>'

    def handle(self, *args, **options):
        file_name = args[0]
        with open(file_name) as input_file:
            text = unicode(input_file.readline().strip(),'utf-8')
        job = arg[1]
        description = unicode(input_file.readline().strip(),'utf-8')
        recipients = [line.strip() for line in input_file]
        send_messages(recipients, text=text, job=job, description=description, force=False)
