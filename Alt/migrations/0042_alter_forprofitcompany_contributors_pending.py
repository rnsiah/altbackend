# Generated by Django 3.2.7 on 2021-10-20 00:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0022_companynewsupdate'),
        ('Alt', '0041_forprofitcompany_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='forprofitcompany',
            name='contributors_pending',
            field=models.ManyToManyField(blank=True, related_name='contributors_pending', to='api.UserProfile'),
        ),
    ]
