# Generated by Django 3.2.4 on 2021-09-21 01:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Alt', '0028_nonprofitbalance_last_transaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='atrocitybalance',
            name='last_transaction',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
