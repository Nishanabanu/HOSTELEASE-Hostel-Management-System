# Generated by Django 5.0.7 on 2024-08-06 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hostel_project', '0013_remove_department_duration_course_duration_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='department',
            name='type',
        ),
        migrations.AddField(
            model_name='course',
            name='type',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
    ]