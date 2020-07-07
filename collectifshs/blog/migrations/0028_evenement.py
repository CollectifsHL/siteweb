# Generated by Django 2.2.9 on 2020-02-17 12:56

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0027_auto_20200122_2125'),
    ]

    operations = [
        migrations.CreateModel(
            name='Evenement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(default=django.utils.timezone.now, help_text='jj/mm/année', verbose_name='Date')),
                ('end_time', models.DateTimeField(blank=True, help_text='jj/mm/année', null=True, verbose_name='Date de fin (optionnel pour un evenement sur plusieurs jours)')),
                ('article', models.ForeignKey(help_text="L'evenement doit etre associé à un article existant (sinon créez un article avec une date)", on_delete=django.db.models.deletion.CASCADE, to='blog.Article')),
            ],
            options={
                'unique_together': {('article', 'start_time')},
            },
        ),
    ]
