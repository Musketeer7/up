# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sms', '0005_auto_20150215_1546'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='description',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='message',
            name='error',
            field=models.CharField(null=True, default='', max_length=50, verbose_name='Error'),
        ),
        migrations.AlterField(
            model_name='message',
            name='state',
            field=models.CharField(verbose_name='State', default='S', max_length=1, choices=[('P', 'Pending'), ('F', 'Failed'), ('S', 'Sent'), ('D', 'Delivered')], db_index=True),
        ),
    ]
