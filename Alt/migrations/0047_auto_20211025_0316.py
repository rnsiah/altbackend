# Generated by Django 3.2.7 on 2021-10-25 03:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Alt', '0046_alter_nonprofitproject_atrocity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='forprofitcompany',
            name='atrocities',
            field=models.ManyToManyField(blank=True, related_name='company', to='Alt.Atrocity'),
        ),
        migrations.AlterField(
            model_name='forprofitcompany',
            name='nonprofits',
            field=models.ManyToManyField(blank=True, related_name='company', to='Alt.NonProfit'),
        ),
    ]