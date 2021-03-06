# Generated by Django 2.2.8 on 2020-07-07 19:58

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('marcheLibre', '0015_auto_20190409_1917'),
    ]

    operations = [
        migrations.CreateModel(
            name='InscriptionNewsletter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('date_inscription', models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscription")),
            ],
        ),
        migrations.CreateModel(
            name='Suivis',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom_suivi', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='profil',
            name='cotisation_a_jour',
            field=models.BooleanField(default=False, verbose_name='Cotisation à jour'),
        ),
        migrations.AddField(
            model_name='profil',
            name='date_notifications',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date de validation des notifications'),
        ),
        migrations.AddField(
            model_name='profil',
            name='is_jardinpartage',
            field=models.BooleanField(default=False, verbose_name='Je suis intéressé.e par les jardins partagés'),
        ),
        migrations.AddField(
            model_name='profil',
            name='statut_adhesion_rtg',
            field=models.IntegerField(choices=[('', '-----------'), (0, "Je souhaite devenir membre de l'association 'Ramene Ta Graine' et utiliser le site"), (1, "Je souhaite utiliser le site, mais ne pas devenir membre de l'association RTG"), (2, "Je suis déjà membre de l'association Ramene Ta Graine")], default='0'),
        ),
        migrations.AlterField(
            model_name='produit',
            name='date_debut',
            field=models.DateField(blank=True, null=True, verbose_name='Débute le (jj/mm/an)'),
        ),
        migrations.AlterField(
            model_name='produit',
            name='date_expiration',
            field=models.DateField(blank=True, null=True, verbose_name='Expire le (jj/mm/an)'),
        ),
        migrations.AlterField(
            model_name='produit',
            name='estPublique',
            field=models.BooleanField(default=False, verbose_name='Publique (cochez) ou Interne (décochez) [réservé aux membres collectifshl]'),
        ),
        migrations.AlterField(
            model_name='produit',
            name='prix',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='produit',
            name='unite_prix',
            field=models.CharField(choices=[('don', 'don'), ('troc', 'troc'), ('pret', 'prêt'), ('G1', 'G1'), ('Soudaqui', 'Soudaqui'), ('SEL', 'SEL'), ('JEU', 'JEU'), ('HE', 'heureEntraide'), ('Autre', 'A négocier')], default='lliure', max_length=8, verbose_name='monnaie'),
        ),
        migrations.AlterField(
            model_name='produit_service',
            name='souscategorie',
            field=models.CharField(choices=[('jardinage', 'jardinage'), ('éducation', 'éducation'), ('santé', 'santé'), ('bricolage', 'bricolage'), ('informatique', 'informatique'), ('hebergement', 'hebergement'), ('cuisine', 'cuisine'), ('batiment', 'batiment'), ('mécanique', 'mécanique'), ('autre', 'autre')], default='j', max_length=20),
        ),
        migrations.AlterField(
            model_name='profil',
            name='competences',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='profil',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='profil',
            name='inscrit_newsletter',
            field=models.BooleanField(default=False, verbose_name="J'accepte de recevoir des emails de CollectifsHL"),
        ),
        migrations.AlterField(
            model_name='profil',
            name='pseudo_june',
            field=models.CharField(blank=True, default=None, max_length=50, null=True, verbose_name='(optionnel) pseudo Monnaie Libre'),
        ),
        migrations.AlterField(
            model_name='profil',
            name='statut_adhesion',
            field=models.IntegerField(choices=[('', '-----------'), (0, "Je souhaite devenir membre du collectif 'CollectifsHL' et utiliser le site"), (1, "Je souhaite utiliser le site, mais ne pas devenir membre de les collectifs Hameaux Légers"), (2, "Je suis déjà membre de les collectifs Hameaux Légers")], default='0'),
        ),
        migrations.CreateModel(
            name='MessageGeneralRTG',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('auteur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MessageGeneralCollectifsHL',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('auteur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Adhesion_collectifshl',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_cotisation', models.DateField(verbose_name='Date de la cotisation')),
                ('montant', models.CharField(blank=True, max_length=50, verbose_name="Montant de l'adhesion")),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
