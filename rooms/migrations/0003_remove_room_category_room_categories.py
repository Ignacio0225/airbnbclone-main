# Generated by Django 5.1.6 on 2025-03-13 13:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0001_initial'),
        ('rooms', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='room',
            name='category',
        ),
        migrations.AddField(
            model_name='room',
            name='categories',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='rooms', to='categories.category'),
        ),
    ]
