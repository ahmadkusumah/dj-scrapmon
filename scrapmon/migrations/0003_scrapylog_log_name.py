# Generated by Django 2.0.1 on 2018-01-15 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scrapmon', '0002_auto_20180115_0927'),
    ]

    operations = [
        migrations.AddField(
            model_name='scrapylog',
            name='log_name',
            field=models.CharField(default=None, max_length=200),
        ),
    ]
