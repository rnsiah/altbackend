# Generated by Django 3.2.7 on 2021-09-21 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Alt', '0029_atrocitybalance_last_transaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyatrocityrelationship',
            name='total_raised',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='companynonprofitrelationship',
            name='total_raised',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]
