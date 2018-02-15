# Generated by Django 2.0.2 on 2018-02-15 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PasscodeVerify',
            fields=[
                ('mobile', models.IntegerField(primary_key=True, serialize=False)),
                ('device_ident', models.CharField(max_length=20)),
                ('passcode', models.CharField(default='0000', max_length=4)),
                ('is_verified', models.BooleanField(default=False)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserBase',
            fields=[
                ('mobile', models.IntegerField(primary_key=True, serialize=False)),
                ('device_ident', models.CharField(max_length=50)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('token', models.CharField(default='xyz', max_length=50)),
                ('is_active', models.BooleanField(default=False)),
            ],
        ),
    ]