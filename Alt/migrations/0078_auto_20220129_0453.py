# Generated by Django 3.2.7 on 2022-01-29 04:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Alt', '0077_shirt_variations'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shirt',
            name='variations',
        ),
        migrations.AddField(
            model_name='shirtvariations',
            name='shirt',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Alt.shirt'),
        ),
    ]