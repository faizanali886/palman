# Generated by Django 4.2.5 on 2023-09-26 22:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='botid',
            field=models.PositiveIntegerField(blank=True, choices=[(1, 1)], null=True),
        ),
    ]
