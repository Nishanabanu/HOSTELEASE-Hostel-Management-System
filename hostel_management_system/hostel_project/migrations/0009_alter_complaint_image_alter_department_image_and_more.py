# Generated by Django 5.0.7 on 2024-08-03 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hostel_project', '0008_alter_warden_hostel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='complaint',
            name='image',
            field=models.ImageField(upload_to='complaints/'),
        ),
        migrations.AlterField(
            model_name='department',
            name='image',
            field=models.ImageField(upload_to='department_images/'),
        ),
        migrations.AlterField(
            model_name='hostel',
            name='image',
            field=models.ImageField(upload_to='hostel_images/'),
        ),
        migrations.AlterField(
            model_name='room',
            name='image',
            field=models.ImageField(upload_to='room_images/'),
        ),
        migrations.AlterField(
            model_name='student',
            name='image',
            field=models.ImageField(upload_to='student_images/'),
        ),
        migrations.AlterField(
            model_name='tutor',
            name='image',
            field=models.ImageField(upload_to='tutor_images/'),
        ),
        migrations.AlterField(
            model_name='warden',
            name='image',
            field=models.ImageField(upload_to='warden_images/'),
        ),
    ]