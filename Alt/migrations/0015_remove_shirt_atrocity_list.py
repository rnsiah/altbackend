# Generated by Django 3.2.4 on 2021-08-23 23:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Alt', '0014_shirt_atrocity_list'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shirt',
            name='atrocity_list',
        ),
    ]
