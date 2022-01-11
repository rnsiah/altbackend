# Generated by Django 3.2.7 on 2021-10-15 02:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Alt', '0034_nonprofitatrocityrelationship_nonprofitproject'),
    ]

    operations = [
        migrations.AddField(
            model_name='checkoutaddress',
            name='special_directions',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='companynonprofitrelationship',
            name='donation_limit',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]