# Generated by Django 2.2.8 on 2020-07-07 19:15

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import stdimage.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profil',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('site_web', models.URLField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('competences', models.TextField(blank=True, null=True)),
                ('avatar', stdimage.models.StdImageField(blank=True, null=True, upload_to='avatars/')),
                ('date_registration', models.DateTimeField(editable=False, verbose_name='Date de création')),
                ('pseudo_june', models.CharField(blank=True, default=None, max_length=50, null=True, verbose_name='(optionnel) pseudo Monnaie Libre')),
                ('inscrit_newsletter', models.BooleanField(default=False, verbose_name="J'accepte de recevoir des emails de CollectifsHL")),
                ('statut_adhesion', models.IntegerField(choices=[('', '-----------'), (0, "Je souhaite devenir membre de l'association 'PermaCat' et utiliser le site"), (1, "Je souhaite utiliser le site, mais ne pas devenir membre de l'association CollectifsHL"), (2, "Je suis déjà membre de l'association CollectifsHL")], default='0')),
                ('statut_adhesion_rtg', models.IntegerField(choices=[('', '-----------'), (0, "Je souhaite devenir membre de l'association 'Ramene Ta Graine' et utiliser le site"), (1, "Je souhaite utiliser le site, mais ne pas devenir membre de l'association RTG"), (2, "Je suis déjà membre de l'association Ramene Ta Graine")], default='0')),
                ('cotisation_a_jour', models.BooleanField(default=False, verbose_name='Cotisation à jour')),
                ('accepter_conditions', models.BooleanField(default=False, verbose_name="J'ai lu et j'accepte les conditions d'utilisation du site")),
                ('accepter_annuaire', models.BooleanField(default=True, verbose_name="J'accepte d'apparaitre dans l'annuaire du site et la carte et rend mon profil visible par tous")),
                ('is_jardinpartage', models.BooleanField(default=False, verbose_name='Je suis intéressé.e par les jardins partagés')),
                ('date_notifications', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date de validation des notifications')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Adresse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rue', models.CharField(blank=True, max_length=200, null=True)),
                ('code_postal', models.CharField(blank=True, default='66000', max_length=5, null=True)),
                ('commune', models.CharField(blank=True, default='Perpignan', max_length=50, null=True)),
                ('latitude', models.FloatField(blank=True, default='42.6976', null=True)),
                ('longitude', models.FloatField(blank=True, default='2.8954', null=True)),
                ('pays', models.CharField(blank=True, default='France', max_length=12, null=True)),
                ('telephone', models.CharField(blank=True, max_length=10, validators=[django.core.validators.RegexValidator(message='Le numero de telephone doit contenir 10 chiffres', regex='^\\d{9,10}$')])),
            ],
        ),
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.CharField(max_length=100)),
                ('date_creation', models.DateTimeField(auto_now_add=True, verbose_name='Date de parution')),
                ('date_dernierMessage', models.DateTimeField(auto_now=True, verbose_name='Date de Modification')),
                ('dernierMessage', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('profil1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profil1', to=settings.AUTH_USER_MODEL)),
                ('profil2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profil2', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-date_dernierMessage',),
            },
        ),
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
        migrations.CreateModel(
            name='Produit_aliment',
            fields=[
                ('produit_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='marcheLibre.Produit')),
                ('couleur', models.CharField(choices=[('#e6f2ff', '#e6f2ff')], default='#e6f2ff', max_length=20)),
                ('souscategorie', models.CharField(choices=[('legumes', 'legumes'), ('fruits', 'fruits'), ('aromates', 'aromates'), ('champignons', 'champignons'), ('boisson', 'boisson'), ('herbes', 'herbes'), ('condiments', 'condiments'), ('viande', 'viande'), ('poisson', 'poisson'), ('boulangerie', 'boulangerie'), ('patisserie', 'patisserie'), ('autre', 'autre')], default='l', max_length=20)),
                ('type_prix', models.CharField(choices=[('kg', 'kg'), ('100g', '100g'), ('10g', '10g'), ('g', 'g'), ('un', 'unité'), ('li', 'litre')], default='kg', max_length=20, verbose_name='par')),
            ],
            bases=('marcheLibre.produit',),
        ),
        migrations.CreateModel(
            name='Produit_objet',
            fields=[
                ('produit_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='marcheLibre.Produit')),
                ('couleur', models.CharField(choices=[('#ffffe6', '#ffffe6')], default='#ffffe6', max_length=20)),
                ('souscategorie', models.CharField(choices=[('jardinage', 'jardinage'), ('outillage', 'outillage'), ('vehicule', 'vehicule'), ('multimedia', 'multimedia'), ('mobilier', 'mobilier'), ('construction', 'construction'), ('instrument', 'instrument'), ('autre', 'autre')], default='j', max_length=20)),
                ('type_prix', models.CharField(choices=[('kg', 'kg'), ('100g', '100g'), ('10g', '10g'), ('g', 'g'), ('un', 'unité'), ('li', 'litre')], default='kg', max_length=20, verbose_name='par')),
            ],
            bases=('marcheLibre.produit',),
        ),
        migrations.CreateModel(
            name='Produit_service',
            fields=[
                ('produit_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='marcheLibre.Produit')),
                ('couleur', models.CharField(choices=[('#ffe6e6', '#ffe6e6')], default='#ffe6e6', max_length=20)),
                ('souscategorie', models.CharField(choices=[('jardinage', 'jardinage'), ('éducation', 'éducation'), ('santé', 'santé'), ('bricolage', 'bricolage'), ('informatique', 'informatique'), ('hebergement', 'hebergement'), ('cuisine', 'cuisine'), ('batiment', 'batiment'), ('mécanique', 'mécanique'), ('autre', 'autre')], default='j', max_length=20)),
                ('type_prix', models.CharField(choices=[('h', 'heure'), ('un', 'unité')], default='h', max_length=20, verbose_name='par')),
            ],
            bases=('marcheLibre.produit',),
        ),
        migrations.CreateModel(
            name='Produit_vegetal',
            fields=[
                ('produit_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='marcheLibre.Produit')),
                ('couleur', models.CharField(choices=[('#e6ffe6', '#e6ffe6')], default='#e6ffe6', max_length=20)),
                ('souscategorie', models.CharField(choices=[('plantes', 'plantes'), ('graines', 'graines'), ('fleurs', 'fleurs'), ('jeunes plants', 'jeunes plants'), ('purins', 'purins'), ('autre', 'autre')], default='p', max_length=20)),
                ('type_prix', models.CharField(choices=[('kg', 'kg'), ('100g', '100g'), ('10g', '10g'), ('g', 'g'), ('un', 'unité'), ('li', 'litre')], default='kg', max_length=20, verbose_name='par')),
            ],
            bases=('marcheLibre.produit',),
        ),
        migrations.CreateModel(
            name='Produit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_creation', models.DateTimeField(editable=False, verbose_name='Date de parution')),
                ('date_debut', models.DateField(blank=True, null=True, verbose_name='Débute le (jj/mm/an)')),
                ('date_expiration', models.DateField(blank=True, null=True, verbose_name='Expire le (jj/mm/an)')),
                ('nom_produit', models.CharField(max_length=250, verbose_name="Titre de l'annonce")),
                ('description', models.TextField(blank=True, null=True)),
                ('stock_initial', models.FloatField(default=1, max_length=250, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Quantité disponible')),
                ('stock_courant', models.FloatField(default=1, max_length=250, validators=[django.core.validators.MinValueValidator(0)])),
                ('prix', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8, validators=[django.core.validators.MinValueValidator(0)])),
                ('unite_prix', models.CharField(choices=[('don', 'don'), ('troc', 'troc'), ('pret', 'prêt'), ('G1', 'G1'), ('Soudaqui', 'Soudaqui'), ('SEL', 'SEL'), ('JEU', 'JEU'), ('HE', 'heureEntraide'), ('Autre', 'A négocier')], default='lliure', max_length=8, verbose_name='monnaie')),
                ('categorie', models.CharField(choices=[('aliment', 'aliment'), ('vegetal', 'végétal'), ('service', 'service'), ('objet', 'objet')], default='aliment', max_length=20)),
                ('estUneOffre', models.BooleanField(default=True, verbose_name='Offre (cochez) ou Demande (décochez)')),
                ('estPublique', models.BooleanField(default=False, verbose_name='Publique (cochez) ou Interne (décochez) [réservé aux membres collectifshl]')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Panier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_creation', models.DateTimeField(editable=False, verbose_name='date de création ')),
                ('checked_out', models.BooleanField(default=False, verbose_name='checked out')),
                ('etat', models.CharField(choices=[('a', 'en cours'), ('ok', 'validé'), ('t', 'terminé'), ('c', 'annulé')], default='a', max_length=8, verbose_name='état')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'panier',
                'verbose_name_plural': 'paniers',
                'ordering': ('-date_creation',),
            },
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
            name='MessageGeneral',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('auteur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('auteur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='marcheLibre.Conversation')),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantite', models.DecimalField(decimal_places=3, max_digits=6, verbose_name='quantite')),
                ('panier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='marcheLibre.Panier', verbose_name='panier')),
                ('produit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='marcheLibre.Produit')),
            ],
            options={
                'verbose_name': 'item',
                'verbose_name_plural': 'items',
                'ordering': ('panier',),
            },
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
        migrations.AddField(
            model_name='profil',
            name='adresse',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='marcheLibre.Adresse'),
        ),
        migrations.AddField(
            model_name='profil',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='profil',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]
