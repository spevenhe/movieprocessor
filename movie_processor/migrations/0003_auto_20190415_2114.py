# Generated by Django 2.1.5 on 2019-04-16 01:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('movie_processor', '0002_comment_movie'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='price',
            new_name='movie',
        ),
    ]
