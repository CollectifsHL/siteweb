# Generated by Django 2.2.8 on 2020-07-07 19:15

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Atelier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('categorie', models.CharField(choices=[('0', 'Permaculture'), ('1', 'Bricolage'), ('2', 'Cuisine'), ('3', 'Bien-être'), ('4', 'Musique'), ('5', 'Autre...')], default='0', max_length=30, verbose_name='categorie')),
                ('statut', models.CharField(choices=[('0', 'proposition'), ('1', "accepté, en cours d'organisation")], default='proposition', max_length=30, verbose_name="Statut de l'atelier")),
                ('titre', models.CharField(max_length=120, verbose_name="Titre de l'atelier")),
                ('slug', models.SlugField(default=uuid.uuid4, max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('materiel', models.TextField(blank=True, null=True, verbose_name='Matériel nécessaire')),
                ('outils', models.TextField(blank=True, null=True, verbose_name='Outils nécessaire')),
                ('referent', models.CharField(blank=True, max_length=120, null=True, verbose_name='Référent(e.s)')),
                ('date_atelier', models.DateField(blank=True, default=django.utils.timezone.now, help_text='(jj/mm/an)', null=True, verbose_name="Date prévue (affichage dans l'agenda)")),
                ('heure_atelier', models.TimeField(blank=True, default='17:00', help_text='(hh:mm)', null=True, verbose_name='Heure prévue')),
                ('date_creation', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date de parution')),
                ('date_modification', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date de modification')),
                ('date_dernierMessage', models.DateTimeField(auto_now=True, verbose_name='Date du dernier message')),
                ('dernierMessage', models.CharField(blank=True, default=None, help_text='Heure prévue (hh:mm)', max_length=100, null=True)),
                ('duree_prevue', models.TimeField(blank=True, default='02:00', help_text="Durée de l'atelier estimée", null=True, verbose_name='Durée prévue')),
                ('tarif_par_personne', models.CharField(default='gratuit', help_text="Tarif de l'atelier par personne", max_length=30, verbose_name="Tarif de l'atelier par personne")),
            ],
            options={
                'ordering': ('-date_creation',),
            },
        ),
        migrations.CreateModel(
            name='CommentaireAtelier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('commentaire', models.TextField()),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='InscriptionAtelier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_inscription', models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscritpion")),
                ('atelier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ateliers.Atelier')),
            ],
        ),
    ]
