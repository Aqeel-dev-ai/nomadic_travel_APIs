# Generated by Django 5.0.2 on 2025-06-11 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tour',
            name='number_of_adults',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='tour',
            name='number_of_children',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='tour',
            name='number_of_kids',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
