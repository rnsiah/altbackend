# Generated by Django 3.2.7 on 2022-03-03 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0054_auto_20220303_1202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='balance',
            name='balance',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=6),
        ),
        migrations.AlterField(
            model_name='companymatchdonation',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=5),
        ),
        migrations.AlterField(
            model_name='userdonation',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=5),
        ),
    ]
