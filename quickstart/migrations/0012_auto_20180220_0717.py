# Generated by Django 2.0.2 on 2018-02-20 07:17

from django.db import migrations, models
import quickstart.models


class Migration(migrations.Migration):

    dependencies = [
        ('quickstart', '0011_auto_20180220_0637'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='device_ident',
            field=models.CharField(blank=True, default=quickstart.models.my_random_key, max_length=50),
        ),
    ]
