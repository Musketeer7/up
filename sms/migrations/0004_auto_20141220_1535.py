# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sms', '0003_auto_20141217_0047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='job_type',
            field=models.CharField(max_length=80, null=True, verbose_name='Job Type'),
            preserve_default=True,
        ),
    ]
