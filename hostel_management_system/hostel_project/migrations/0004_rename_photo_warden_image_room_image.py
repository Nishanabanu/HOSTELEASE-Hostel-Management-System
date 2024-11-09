# Generated by Django 5.0.7 on 2024-07-31 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hostel_project', '0003_hostel_image_hostel_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='warden',
            old_name='photo',
            new_name='image',
        ),
        migrations.AddField(
            model_name='room',
            name='image',
            field=models.FileField(default=1, upload_to='room_image/'),
            preserve_default=False,
        ),
    ]
