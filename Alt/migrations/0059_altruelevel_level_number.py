# Generated by Django 3.2.7 on 2021-10-27 06:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Alt', '0058_auto_20211027_0551'),
    ]

    operations = [
        migrations.AddField(
            model_name='altruelevel',
            name='level_number',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
