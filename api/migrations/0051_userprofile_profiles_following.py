# Generated by Django 3.2.7 on 2022-02-18 02:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0050_nonprofitrequest_requestvotes'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='profiles_following',
            field=models.ManyToManyField(to='api.UserProfile'),
        ),
    ]
