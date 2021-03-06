# Generated by Django 2.2.8 on 2020-07-07 19:15

from django.db import migrations, models
import django.utils.timezone
import taggit.managers
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('taggit', '0003_taggeditem_add_unique_index'),
    ]

    operations = [
        migrations.CreateModel(
            name='Atelier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('categorie', models.CharField(choices=[('0', 'Observation'), ('1', 'Experience'), ('2', 'Jardinage')], default='0', max_length=30, verbose_name='categorie')),
                ('titre', models.CharField(max_length=100)),
                ('slug', models.SlugField(default=uuid.uuid4, max_length=100)),
                ('contenu', models.TextField(null=True)),
                ('age', models.CharField(choices=[('0', '3-6 ans'), ('1', '7-11 ans'), ('2', '12 ans et plus'), ('3', '3-11ans'), ('4', 'Tout public')], default='0', max_length=30, verbose_name='age')),
                ('difficulte', models.CharField(choices=[('0', 'facile'), ('1', 'moyen'), ('2', 'difficile')], default='0', max_length=30, verbose_name='difficulté')),
                ('budget', models.CharField(choices=[('0', '0'), ('1', '1'), ('2', '2'), ('3', '3')], default='0', max_length=30, verbose_name='budget')),
                ('temps', models.CharField(choices=[('1', '1h'), ('2', '2h'), ('3', '3h'), ('4', '4h'), ('5', '6h'), ('6', '1 journée'), ('7', 'plusieurs jours'), ('8', 'plusieurs mois')], default='0', max_length=30, verbose_name='temps')),
                ('date_creation', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date de parution')),
                ('date_modification', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date de modification')),
            ],
            options={
                'ordering': ('-date_creation',),
            },
        ),
        migrations.CreateModel(
            name='CommentaireFiche',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('commentaire', models.TextField()),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Fiche',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('categorie', models.CharField(choices=[('0', 'Bases de la permaculture'), ('1', 'Conception du jardin'), ('2', 'Réalisation du jardin'), ('3', 'Récolter')], default='0', max_length=30, verbose_name='categorie')),
                ('statut', models.CharField(choices=[('0', 'proposition'), ('1', "en cours d'écriture"), ('2', 'achevée mais pas validée'), ('3', 'validée')], default='proposition', max_length=30, verbose_name='statut de la fiche')),
                ('numero', models.PositiveIntegerField(default=1)),
                ('titre', models.CharField(max_length=120)),
                ('slug', models.SlugField(default=uuid.uuid4, max_length=100)),
                ('contenu', models.TextField(blank=True, null=True)),
                ('objectif', models.TextField(blank=True, null=True)),
                ('en_savoir_plus', models.TextField(blank=True, null=True)),
                ('date_creation', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date de parution')),
                ('date_modification', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date de modification')),
                ('date_dernierMessage', models.DateTimeField(auto_now=True, verbose_name='Date du dernier message')),
                ('dernierMessage', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('tags', taggit.managers.TaggableManager(blank=True, help_text='Une liste de mots clés, séparés par des virgules.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Mots-clés')),
            ],
            options={
                'ordering': ('-date_creation',),
            },
        ),
    ]
