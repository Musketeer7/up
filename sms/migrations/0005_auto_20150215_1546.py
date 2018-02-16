# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sms', '0004_auto_20141220_1535'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='state',
            field=models.CharField(default=b'S', max_length=1, verbose_name='State', db_index=True, choices=[(b'P', 'Pending'), (b'F', 'Failed'), (b'S', 'Sent'), (b'D', 'Delivered')]),
            preserve_default=True,
        ),
    ]
