# Generated by Django 3.2.7 on 2021-10-15 02:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0021_auto_20211015_0231'),
        ('Alt', '0036_auto_20211015_0216'),
    ]

    operations = [
        migrations.AddField(
            model_name='nonprofit',
            name='contributors',
            field=models.ManyToManyField(related_name='contributors', to='api.UserProfile'),
        ),
    ]