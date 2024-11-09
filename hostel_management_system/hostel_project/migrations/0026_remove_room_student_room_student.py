# Generated by Django 5.0.7 on 2024-09-15 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hostel_project', '0025_alter_room_hostel'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='room',
            name='STUDENT',
        ),
        migrations.AddField(
            model_name='room',
            name='STUDENT',
            field=models.ManyToManyField(blank=True, related_name='rooms', to='hostel_project.student'),
        ),
    ]
