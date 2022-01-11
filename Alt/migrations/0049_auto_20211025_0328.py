# Generated by Django 3.2.7 on 2021-10-25 03:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Alt', '0048_auto_20211025_0319'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nonprofitproject',
            name='atrocity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='np_project_atrocity', to='Alt.atrocity'),
        ),
        migrations.AlterField(
            model_name='nonprofitproject',
            name='cause',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='np_project_cause', to='Alt.category'),
        ),
        migrations.AlterField(
            model_name='nonprofitproject',
            name='nonprofit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='np_project_nonprofit', to='Alt.nonprofit'),
        ),
    ]