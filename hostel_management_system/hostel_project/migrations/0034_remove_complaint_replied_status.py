# Generated by Django 5.0.7 on 2024-10-26 15:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hostel_project', '0033_warden_date_of_retirement_warden_is_retired_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='complaint',
            name='replied_status',
        ),
    ]