# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('sms', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='Message',
            name='description',
            field=models.CharField(default=b'', max_length=200, verbose_name='Description', blank=True),
            preserve_default=True,
        ),
    ]
