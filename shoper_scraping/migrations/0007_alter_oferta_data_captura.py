# Generated by Django 4.0.4 on 2022-05-23 03:27

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shoper_scraping', '0006_alter_oferta_data_captura'),
    ]

    operations = [
        migrations.AlterField(
            model_name='oferta',
            name='data_captura',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
