# Generated by Django 3.2.7 on 2022-03-03 02:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Alt', '0086_auto_20220220_0443'),
    ]

    operations = [
        migrations.AddField(
            model_name='companydonation',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='company_donation', to='Alt.nonprofitproject'),
        ),
    ]
