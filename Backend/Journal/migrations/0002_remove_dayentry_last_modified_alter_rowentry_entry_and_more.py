# Generated by Django 5.2 on 2025-04-14 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Journal", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="dayentry",
            name="last_modified",
        ),
        migrations.AlterField(
            model_name="rowentry",
            name="entry",
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name="rowentry",
            name="time",
            field=models.TimeField(),
        ),
    ]
