# Generated by Django 3.2.7 on 2021-10-15 06:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Alt', '0039_forprofitcompany_contributors_pending'),
        ('api', '0021_auto_20211015_0231'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyNewsUpdate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='companyupdate', to='Alt.forprofitcompany')),
            ],
        ),
    ]
