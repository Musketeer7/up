# Generated by Django 2.0.2 on 2018-02-20 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quickstart', '0014_auto_20180220_0904'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='device_ident',
            field=models.CharField(max_length=50),
        ),
    ]