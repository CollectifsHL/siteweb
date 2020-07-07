# Generated by Django 2.1.7 on 2019-04-06 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marcheLibre', '0011_auto_20190406_1156'),
    ]

    operations = [
        migrations.AddField(
            model_name='profil',
            name='accepter_annuaire',
            field=models.BooleanField(default=True, verbose_name="J'accepte d'apparaitre dans l'annuaire du site et rend mon profil visible par tous"),
        ),
        migrations.AddField(
            model_name='conversation',
            name='dernierMessage',
            field=models.CharField(blank=True, default=None, max_length=100, null=True),
        ),
    ]