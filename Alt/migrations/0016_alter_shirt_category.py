# Generated by Django 3.2.4 on 2021-08-29 03:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Alt', '0015_remove_shirt_atrocity_list'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shirt',
            name='category',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='shirt', to='Alt.category'),
        ),
    ]