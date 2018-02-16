# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField(verbose_name='Text')),
                ('to', models.CharField(max_length=16, verbose_name='To')),
                ('state', models.CharField(default=b'S', max_length=1, verbose_name='State', db_index=True, choices=[(b'F', 'Failed'), (b'S', 'Sent'), (b'D', 'Delivered')])),
                ('reference_code', models.CharField(max_length=20, null=True, verbose_name='Reference Code')),
                ('error', models.CharField(default=b'', max_length=30, null=True, verbose_name='Error')),
                ('job_type', models.CharField(max_length=20, null=True, verbose_name='Job Type')),
                ('created', models.DateTimeField(default=timezone.now, verbose_name='Created Time')),
                ('backend', models.CharField(max_length=8, verbose_name='Backend')),
            ],
            options={
                'verbose_name': 'Message',
                'verbose_name_plural': 'Messages',
            },
            bases=(models.Model,),
        ),
    ]
