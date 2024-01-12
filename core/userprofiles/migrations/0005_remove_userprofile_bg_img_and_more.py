# Generated by Django 4.1 on 2024-01-11 14:38

from django.db import migrations, models
import userprofiles.models


class Migration(migrations.Migration):

    dependencies = [
        ("userprofiles", "0004_alter_userprofile_bio_title"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userprofile",
            name="bg_img",
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="profile_pic",
            field=models.ImageField(
                blank=True,
                default="",
                null=True,
                upload_to=userprofiles.models.upload_image_path,
            ),
        ),
    ]
