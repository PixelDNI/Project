# Generated by Django 5.0 on 2023-12-19 10:45

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminMathTrainer', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authorprofile',
            name='reputation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reputation', to=settings.AUTH_USER_MODEL),
        ),
    ]