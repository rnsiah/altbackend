# Generated by Django 3.2.7 on 2021-10-27 03:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0028_alter_altruepoints_balance'),
    ]

    operations = [
        migrations.AddField(
            model_name='altruepoints',
            name='last_transaction',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.DeleteModel(
            name='CompanyNewsUpdate',
        ),
    ]
