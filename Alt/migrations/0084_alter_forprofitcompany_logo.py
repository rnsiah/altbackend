# Generated by Django 3.2.7 on 2022-02-05 02:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Alt', '0083_alter_forprofitcompany_year_started'),
    ]

    operations = [
        migrations.AlterField(
            model_name='forprofitcompany',
            name='logo',
            field=models.CharField(blank=True, default='https://i.ibb.co/yPCqbSG/altruecompany-placeholder.png', max_length=200, null=True),
        ),
    ]
