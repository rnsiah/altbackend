# Generated by Django 3.2.7 on 2022-01-30 23:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0049_auto_20211121_0117'),
        ('Alt', '0078_auto_20220129_0453'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profileimage',
            name='id',
        ),
        migrations.AlterField(
            model_name='profileimage',
            name='profile',
            field=models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='profile_pic', serialize=False, to='api.userprofile'),
        ),
    ]
