# Generated by Django 3.2.7 on 2021-10-29 23:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Alt', '0064_profileimage_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='profileimage',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='profiles'),
        ),
    ]