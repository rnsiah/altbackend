# Generated by Django 3.2.7 on 2022-04-25 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Alt', '0096_usermatchrelationship'),
    ]

    operations = [
        migrations.AddField(
            model_name='usermatchrelationship',
            name='was_confirmed',
            field=models.BooleanField(default=False),
        ),
    ]
