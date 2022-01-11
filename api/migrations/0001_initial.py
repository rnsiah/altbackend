# Generated by Django 3.2.4 on 2021-06-29 01:45

import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('Alt', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('username', models.CharField(blank=True, max_length=100, null=True)),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('profile_created', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='profile', serialize=False, to='api.user')),
                ('username', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('title', models.CharField(blank=True, max_length=5, null=True)),
                ('dob', models.CharField(blank=True, max_length=12, null=True)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('country', models.CharField(blank=True, max_length=50, null=True)),
                ('city', models.CharField(blank=True, max_length=50, null=True)),
                ('zip', models.CharField(blank=True, max_length=5, null=True)),
                ('qr_code', models.CharField(blank=True, max_length=50, null=True)),
                ('slug', models.SlugField(blank=True, null=True)),
                ('qr_code_img', models.ImageField(blank=True, null=True, upload_to='qr_codes')),
                ('atrocity_list', models.ManyToManyField(blank=True, related_name='UserProfiles', to='Alt.Atrocity')),
                ('nonProfit_list', models.ManyToManyField(blank=True, related_name='UserProfiles', to='Alt.NonProfit')),
                ('shirt_list', models.ManyToManyField(blank=True, related_name='UserProfiles', to='Alt.Shirt', verbose_name='shirts')),
            ],
        ),
        migrations.CreateModel(
            name='Donor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('amount_donated', models.DecimalField(decimal_places=2, max_digits=5)),
                ('donation_category', models.ManyToManyField(blank=True, related_name='category', to='Alt.Category', verbose_name='')),
                ('sent_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='donor', to='api.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='Balance',
            fields=[
                ('account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='balance', serialize=False, to='api.userprofile')),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=4)),
            ],
            options={
                'verbose_name': 'Balance',
                'verbose_name_plural': 'Balances',
            },
        ),
        migrations.CreateModel(
            name='Donation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_charge_id', models.CharField(max_length=100)),
                ('donation_amount', models.DecimalField(decimal_places=2, max_digits=5)),
                ('donation_date', models.DateTimeField(auto_now_add=True)),
                ('donor', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='donation', to='api.donor')),
                ('receiver', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='donation', to='api.balance')),
            ],
        ),
    ]
