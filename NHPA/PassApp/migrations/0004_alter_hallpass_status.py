# Generated by Django 5.0.4 on 2024-05-10 20:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PassApp', '0003_hallpass_is_hidden'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hallpass',
            name='status',
            field=models.BooleanField(default=True),
        ),
    ]
