# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sms', '0002_message_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='error',
            field=models.CharField(default=b'', max_length=50, null=True, verbose_name='Error'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='message',
            name='state',
            field=models.CharField(default=b'S', max_length=1, verbose_name='State', db_index=True, choices=[(b'F', 'Failed'), (b'S', 'Sent'), (b'D', 'Delivered'), (b'N', 'Not Sent')]),
            preserve_default=True,
        ),
    ]
