# Generated by Django 5.0.7 on 2024-10-15 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hostel_project', '0030_payment_notification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='room_number',
            field=models.BigIntegerField(blank=True),
        ),
    ]