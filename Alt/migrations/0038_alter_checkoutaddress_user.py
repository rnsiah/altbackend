# Generated by Django 3.2.7 on 2021-10-15 02:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0021_auto_20211015_0231'),
        ('Alt', '0037_nonprofit_contributors'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checkoutaddress',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.userprofile'),
        ),
    ]
