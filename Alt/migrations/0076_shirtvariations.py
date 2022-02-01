# Generated by Django 3.2.7 on 2022-01-28 22:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Alt', '0075_shirtcolor_hex_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShirtVariations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.CharField(blank=True, max_length=50, null=True)),
                ('color', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Alt.shirtcolor')),
            ],
        ),
    ]