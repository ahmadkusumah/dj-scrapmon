# Generated by Django 2.0.1 on 2018-01-15 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scrapmon', '0006_auto_20180115_1053'),
    ]

    operations = [
        migrations.AddField(
            model_name='scrapylog',
            name='running',
            field=models.NullBooleanField(default=None),
        ),
    ]
