# Generated by Django 4.0.4 on 2022-05-21 15:18

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('shoper_scraping', '0003_remove_oferta_lastupdate_oferta_data_captura'),
    ]

    operations = [
        migrations.AlterField(
            model_name='oferta',
            name='data_captura',
            field=models.DateTimeField(default=datetime.datetime(2022, 5, 21, 15, 18, 58, 125050, tzinfo=utc)),
        ),
    ]
