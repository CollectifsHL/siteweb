# Generated by Django 2.1.3 on 2019-04-09 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marcheLibre', '0014_auto_20190408_2209'),
    ]

    operations = [
        migrations.AlterField(
            model_name='produit',
            name='nom_produit',
            field=models.CharField(max_length=250, verbose_name="Titre de l'annonce"),
        ),
    ]
