from django.db import models
from marcheLibre.models import Profil, Suivis
from django.urls import reverse
from django.utils import timezone
from django.core.mail import send_mass_mail, mail_admins
#from tinymce.models import HTMLField
from django.dispatch import receiver
from django.db.models.signals import post_save

from actstream.models import followers
from marcheLibre.settings import SERVER_EMAIL, DEBUG

class Choix():
    statut_projet = ('prop','Proposition de projet'), ("AGO","Fiche projet soumise à l'AGO"), ('vote','Soumis au vote'), ('accep',"Accepté par l'association"), ('refus',"Refusé par l'association" ),
    type_projet = ('Part','Participation à un évènement'), ('AGO',"Organisation d'une AGO"), ('Projlong','Projet a long terme'), ('Projcourt','Projet a court terme'), ('Projponct','Projet ponctuel'),
    type_annonce = ('1','Annonce'), ('2','Administratif'), ('3','Agenda'), ('4','Chantier participatif'), ('6','Altermarché'), \
                   ('5','Ressources'),  ('0','Autre'),
    couleurs_annonces = {
       # 'Annonce':"#e0f7de", 'Administratif':"#dcc0de", 'Agenda':"#d4d1de", 'Entraide':"#cebacf",
       # 'Chantier':"#d1ecdc",'Jardinage':"#fcf6bd", 'Recette':"#d0f4de", 'Bricolage':"#fff2a0",
       # 'Culture':"#ffc4c8", 'Bon_plan':"#bccacf", 'Point':"#87bfae", 'Autre':"#bcb4b4"

        '15':"#d1ecdc",
        '1':"#D4CF7D",
        '2':"#E0E3AB",
        '3':"#AFE4C1",
        '4':"#fff2a0",
        '5':"#B2AFE4",
        '6':"#d0f4de",
        '7':"#caf9b7",
        '8':"#ced2d3",
        '9':"#349D9B",
        '10':"#bccacf",
        '0':"#87bfae",
        'Autre':"#87bfae",
        '11':"#cebacf",
        '12':"#fffdcc",
        '13':"#daffb3",
        '14':'#ddd0a8',



    }
    couleurs_projets = {
        'Part':"#d0e8da", 'AGO':"#dcc0de", 'Projlong':"#d1d0dc", 'Projcourt':"#ffc09f", 'Projponct':"#e4f9d4",
    }

    def get_couleur(categorie):
        try:
            return Choix.couleurs_annonces[categorie]
        except:
            return Choix.couleurs_annonces["Autre"]

class Article(models.Model):
    categorie = models.CharField(max_length=30,         
        choices=(Choix.type_annonce),
        default='Annonce', verbose_name="categorie")
    titre = models.CharField(max_length=100,)
    auteur = models.ForeignKey(Profil, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=100)
    contenu = models.TextField(null=True)
    date_creation = models.DateTimeField(verbose_name="Date de parution", default=timezone.now)
    date_modification = models.DateTimeField(verbose_name="Date de modification", default=timezone.now)
    estPublic = models.BooleanField(default=False, verbose_name='Public ou réservé aux membres collectifshl')
    estModifiable = models.BooleanField(default=False, verbose_name="Modifiable par n'importe qui")

    date_dernierMessage = models.DateTimeField(verbose_name="Date du dernier message", auto_now=False, default=timezone.now)
    dernierMessage = models.CharField(max_length=100, default=None, blank=True, null=True)
    estArchive = models.BooleanField(default=False, verbose_name="Archiver l'article")

    start_time = models.DateTimeField(verbose_name="Date de début (optionnel, affichage dans l'agenda)", null=True,blank=True, help_text="jj/mm/année")
    end_time = models.DateTimeField(verbose_name="Date de fin (optionnel, pour affichage dans l'agenda)",  null=True,blank=True, help_text="jj/mm/année")

    class Meta:
        ordering = ('-date_creation', )
        
    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse('blog:lireArticle', kwargs={'slug':self.slug})

    def save(self, sendMail=True, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.date_creation = timezone.now()
            if sendMail:
                suivi, created = Suivis.objects.get_or_create(nom_suivi='articles')
                titre = "[CollectifsHL] nouvel article"
                message = " Un nouvel article a été créé : https://collectifshl.herokuapp.com" + self.get_absolute_url() + \
                          "\n\n------------------------------------------------------------------------------" \
                          "\n vous recevez cet email, car vous avez choisi de suivre les articles (en cliquant sur la cloche) sur le site http://collectifshl.herokuapp.com/forum/articles/"
                emails = [suiv.email for suiv in followers(suivi) if
                          self.auteur != suiv and (self.estPublic or suiv.is_collectifshl)]
                if emails and not DEBUG:
                    try:
                        send_mass_mail([(titre, message, SERVER_EMAIL, emails), ])
                    except Exception as inst:
                        mail_admins("erreur mails", titre + "\n" + message + "\n xxx \n" + str(emails) + "\n erreur : " + str(inst))
        else:
            if sendMail:
                titre = "[CollectifsHL] Article actualisé"
                message = "L'article '" + self.titre + "' a été modifié : http://collectifshl.herokuapp.com" + self.get_absolute_url() + \
                          "\n\n------------------------------------------------------------------------------" \
                          "\n vous recevez cet email, car vous avez choisi de suivre cet article sur le site http://collectifshl.herokuapp.com/forum/articles/"

                emails = [suiv.email for suiv in followers(self) if
                          self.auteur != suiv and (self.estPublic or suiv.is_collectifshl)]

                if emails and not DEBUG:
                    try:
                        send_mass_mail([(titre, message, SERVER_EMAIL, emails), ])
                    except Exception as inst:
                        mail_admins("erreur mails", titre + "\n" + message + "\n xxx \n" + str(emails) + "\n erreur : " + str(inst))

        return super(Article, self).save(*args, **kwargs)

    @property
    def get_couleur(self):
        try:
            return Choix.couleurs_annonces[self.categorie]
        except:
            return Choix.couleurs_annonces["Autre"]


class Evenement(models.Model):
    titre = models.CharField(verbose_name="Titre de l'événement (si laissé vide, ce sera le titre de l'article)",
                             max_length=100, null=True, blank=True, default="")
    article = models.ForeignKey(Article, on_delete=models.CASCADE, help_text="L'evenement doit etre associé à un article existant (sinon créez un article avec une date)" )
    start_time = models.DateTimeField(verbose_name="Date", null=False,blank=False, help_text="jj/mm/année" , default=timezone.now)
    end_time = models.DateTimeField(verbose_name="Date de fin (optionnel pour un evenement sur plusieurs jours)",  null=True,blank=True, help_text="jj/mm/année")

    class Meta:
        unique_together = ('article', 'start_time',)

    def get_absolute_url(self):
        return self.article.get_absolute_url()


    @property
    def gettitre(self):
        if not self.titre:
            return self.article.titre
        return self.titre

    @property
    def estPublic(self):
        return self.article.estPublic

class Commentaire(models.Model):
    auteur_comm = models.ForeignKey(Profil, on_delete=models.CASCADE)
    commentaire = models.TextField()
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.__str__()

    def __str__(self):
        return "(" + str(self.id) + ") "+ str(self.auteur_comm) + ": " + str(self.article)

    @property
    def get_edit_url(self):
        return reverse('blog:modifierCommentaireArticle',  kwargs={'id':self.id})

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.date_creation = timezone.now()
            suivi, created = Suivis.objects.get_or_create(nom_suivi='articles')
            titre = "[CollectifsHL] Article commenté"
            message = " Un article auquel vous êtes abonné a été commenté : https://collectifshl.herokuapp.com" + self.article.get_absolute_url() + \
                      "\n\n------------------------------------------------------------------------------" \
                      "\n vous recevez cet email, car vous avez choisi de suivre l'article (en cliquant sur la cloche) sur le site http://collectifshl.herokuapp.com" + self.article.get_absolute_url()
            emails = [suiv.email for suiv in followers(self.article) if
                      self.auteur_comm != suiv and (self.article.estPublic or suiv.is_collectifshl)]
            if emails and not DEBUG:
                try:
                    send_mass_mail([(titre, message, SERVER_EMAIL, emails), ])
                except Exception as inst:
                    mail_admins("erreur mails",
                            titre + "\n" + message + "\n xxx \n" + str(emails) + "\n erreur : " + str(inst))

        return super(Commentaire, self).save(*args, **kwargs)

class Projet(models.Model):
    categorie = models.CharField(max_length=10,
        choices=(Choix.type_projet),
        default='Part', verbose_name="categorie")
    statut = models.CharField(max_length=5,
        choices=(Choix.statut_projet ),
        default='prop', verbose_name="statut")
    titre = models.CharField(max_length=100)
    auteur = models.ForeignKey(Profil, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=100)
    contenu = models.TextField(null=True)
    date_creation = models.DateTimeField(verbose_name="Date de parution", default=timezone.now)
    date_modification = models.DateTimeField(verbose_name="Date de modification", default=timezone.now)
    estPublic = models.BooleanField(default=False, verbose_name='Public (cochez) ou Interne (décochez) [réservé aux membres collectifshl]')
    coresponsable = models.CharField(max_length=150, verbose_name="Référent du projet", default='', null=True, blank=True)
    lien_vote = models.URLField(verbose_name='Lien vers le vote (balotilo.org)', null=True, blank=True, )
    lien_document = models.URLField(verbose_name='Lien vers un document explicatif (en ligne)', default='', null=True, blank=True)
    fichier_projet = models.FileField(upload_to='projets/%Y/%m/', blank=True, default=None, null=True)
    date_fichier = models.DateTimeField(auto_now=True, blank=True)

    date_dernierMessage = models.DateTimeField(verbose_name="Date de Modification", auto_now=True)
    dernierMessage = models.CharField(max_length=100, default="", blank=True, null=True)

    start_time = models.DateTimeField(verbose_name="Date de début (optionnel, pour affichage dans l'agenda)",  null=True,blank=True, help_text="jj/mm/année")
    end_time = models.DateTimeField(verbose_name="Date de fin (optionnel, pour affichage dans l'agenda)",  null=True,blank=True, help_text="jj/mm/année")

    estArchive = models.BooleanField(default=False, verbose_name="Archiver le projet")

    class Meta:
        ordering = ('-date_creation', )

    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse('blog:lireProjet', kwargs={'slug':self.slug})

    def save(self, sendMail = True, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.date_creation = timezone.now()
            titre = "[CollectifsHL] Nouveau Projet !"
            message = " Le projet '" +  self.titre + "' a été créé : https://collectifshl.herokuapp.com" + self.get_absolute_url() + \
                      "\n\n------------------------------------------------------------------------------" \
                      "\n vous recevez cet email, car vous avez choisi de suivre ce projet sur le site http://collectifshl.herokuapp.com/forum/projets/"
            suivi, created = Suivis.objects.get_or_create(nom_suivi='projets')
            emails = [suiv.email for suiv in followers(suivi) if self.auteur != suiv  and (self.estPublic or suiv.is_collectifshl)]

            if emails and not DEBUG:
                try:
                    send_mass_mail([(titre, message, SERVER_EMAIL, emails), ])
                except Exception as inst:
                    mail_admins("erreur mails",  titre + "\n" + message + "\n xxx \n" + str(emails) + "\n erreur : " + str(inst))
        else:
            if sendMail:
                titre = "[CollectifsHL] Projet actualisé"
                message = "Le projet '" + self.titre + "' a été modifié : http://collectifshl.herokuapp.com" + self.get_absolute_url() + \
                          "\n\n------------------------------------------------------------------------------" \
                          "\n vous recevez cet email, car vous avez choisi de suivre ce projet sur le site http://collectifshl.herokuapp.com/forum/articles/"

                emails = [suiv.email for suiv in followers(self) if
                          self.auteur != suiv and (self.estPublic or suiv.is_collectifshl)]

                if emails and not DEBUG:
                    try:
                        send_mass_mail([(titre, message, SERVER_EMAIL, emails), ])
                    except Exception as inst:
                        mail_admins("erreur mails", titre + "\n" + message + "\n xxx \n" + str(emails) + "\n erreur : " + str(inst))

        return super(Projet, self).save(*args, **kwargs)

    @property
    def get_couleur(self):
        try:
            return Choix.couleurs_projets[self.categorie]
        except:
            return Choix.couleurs_annonces["Autre"]


class CommentaireProjet(models.Model):
    auteur_comm = models.ForeignKey(Profil, on_delete=models.CASCADE)
    commentaire = models.TextField(blank=True)
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.__str__()

    def __str__(self):
        return "(" + str(self.id) + ") "+ str(self.auteur_comm) + ": " + str(self.projet)


    @property
    def get_edit_url(self):
        return reverse('blog:modifierCommentaireProjet',  kwargs={'id':self.id})

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            titre = "[CollectifsHL] Projet commenté"
            message = "Le projet '"+ self.projet.titre + "' auquel vous êtes abonné a été commenté : https://collectifshl.herokuapp.com" + self.projet.get_absolute_url() + \
                      "\n\n------------------------------------------------------------------------------" \
                      "\n vous recevez cet email, car vous avez choisi de suivre l'article (en cliquant sur la cloche) sur le site http://collectifshl.herokuapp.com/forum/articles/" + self.projet.get_absolute_url()

            emails = [suiv.email for suiv in followers(self.projet) if
                      self.auteur_comm != suiv and (self.projet.estPublic or suiv.is_collectifshl)]
            if emails and not DEBUG:
                try:
                    send_mass_mail([(titre, message, SERVER_EMAIL, emails), ])
                except Exception as inst:
                    mail_admins("erreur mails",
                                titre + "\n" + message + "\n xxx \n" + str(emails) + "\n erreur : " + str(inst))

        return super(CommentaireProjet, self).save(*args, **kwargs)