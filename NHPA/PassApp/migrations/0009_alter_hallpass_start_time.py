# Generated by Django 5.0.4 on 2024-05-19 09:22

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PassApp', '0008_alter_hallpass_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hallpass',
            name='start_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
