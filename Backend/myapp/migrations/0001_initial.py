# Generated by Django 4.2.5 on 2023-09-26 22:50

import datetime
import django.contrib.auth.models
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bot',
            fields=[
                ('apiSecret', models.CharField(max_length=255)),
                ('botid', models.PositiveIntegerField(unique=True)),
                ('botNumber', models.CharField(max_length=15)),
                ('botLanguage', models.CharField(blank=True, max_length=255)),
                ('botSpeaker', models.CharField(max_length=255)),
                ('maxUser', models.PositiveIntegerField(default=0)),
                ('phone', models.CharField(max_length=15)),
                ('id', models.AutoField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=15, unique=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('email', models.EmailField(max_length=254)),
                ('consumed_credits', models.DurationField(default=datetime.timedelta(0))),
                ('initial_credits', models.DurationField(default=datetime.timedelta(0))),
                ('remaining_credits', models.DurationField(default=datetime.timedelta(0))),
                ('status', models.CharField(choices=[('freetrial', 'Free Trial'), ('active', 'Active'), ('inactive', 'Inactive'), ('blocked', 'Blocked')], default='freetrial', max_length=50)),
                ('location', models.CharField(blank=True, max_length=100)),
                ('botid', models.PositiveIntegerField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Registered User',
                'verbose_name_plural': 'Registered Users',
            },
        ),
        migrations.CreateModel(
            name='Moderator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('username', models.CharField(max_length=100, unique=True)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
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
    ]