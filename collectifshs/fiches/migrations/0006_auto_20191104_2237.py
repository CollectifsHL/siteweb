# Generated by Django 2.1.11 on 2019-11-04 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fiches', '0005_auto_20191104_2236'),
    ]

    operations = [
        migrations.AlterField(
            model_name='atelier',
            name='temps',
            field=models.CharField(choices=[('1', '1h'), ('2', '2h'), ('3', '3h'), ('4', '4h'), ('5', '6h'), ('6', '1 journée'), ('7', 'plusieurs jours'), ('8', 'plusieurs mois')], default='0', max_length=30, verbose_name='temps'),
        ),
    ]
