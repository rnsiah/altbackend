# Generated by Django 3.2.7 on 2021-10-27 03:09

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0029_auto_20211027_0308'),
    ]

    operations = [
        migrations.AlterField(
            model_name='altruepoints',
            name='last_transaction',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 27, 3, 9, 39, 194240, tzinfo=utc)),
        ),
    ]
