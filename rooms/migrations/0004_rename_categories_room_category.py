# Generated by Django 5.1.6 on 2025-03-15 06:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0003_remove_room_category_room_categories'),
    ]

    operations = [
        migrations.RenameField(
            model_name='room',
            old_name='categories',
            new_name='category',
        ),
    ]
