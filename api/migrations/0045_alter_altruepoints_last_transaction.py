# Generated by Django 3.2.7 on 2021-10-29 23:05

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0044_alter_altruepoints_last_transaction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='altruepoints',
            name='last_transaction',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 29, 23, 5, 44, 106640, tzinfo=utc)),
        ),
    ]
