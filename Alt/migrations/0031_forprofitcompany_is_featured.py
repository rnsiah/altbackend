# Generated by Django 3.2.7 on 2021-09-27 04:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Alt', '0030_auto_20210921_0801'),
    ]

    operations = [
        migrations.AddField(
            model_name='forprofitcompany',
            name='is_featured',
            field=models.BooleanField(default=False),
        ),
    ]