# Generated by Django 3.2.7 on 2021-11-29 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Alt', '0067_auto_20211121_0117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nonprofit',
            name='slug',
            field=models.SlugField(blank=True, null=True, unique=True),
        ),
    ]
