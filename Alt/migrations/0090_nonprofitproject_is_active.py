# Generated by Django 3.2.7 on 2022-03-03 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Alt', '0089_auto_20220303_1219'),
    ]

    operations = [
        migrations.AddField(
            model_name='nonprofitproject',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]