# Generated by Django 3.2.7 on 2021-10-20 01:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Alt', '0042_alter_forprofitcompany_contributors_pending'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companycoupon',
            name='coupon_image',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
