# Generated by Django 2.2.8 on 2020-06-15 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vote', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='votation',
            name='type_vote',
            field=models.CharField(choices=[('', '-----------'), ('0', "Vote d'un projet"), ('1', "Vote d'une décision"), ('2', 'Sondage')], default='', max_length=30, verbose_name='Type de vote'),
        ),
    ]
