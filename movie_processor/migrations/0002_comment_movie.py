# Generated by Django 2.1.5 on 2019-04-15 14:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('movie_processor', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='movie',
            field=models.ForeignKey(default=-1, on_delete=django.db.models.deletion.CASCADE, to='movie_processor.Movie'),
            preserve_default=False,
        ),
    ]
