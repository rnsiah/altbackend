# Generated by Django 3.2.4 on 2021-09-18 09:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_userprofile_company_rewards'),
        ('Alt', '0022_auto_20210918_0909'),
    ]

    operations = [
        migrations.AlterField(
            model_name='forprofitcompany',
            name='contributors',
            field=models.ManyToManyField(blank=True, null=True, related_name='forprofitcontributors', to='api.UserProfile'),
        ),
    ]
