# -*- coding: utf-8 -*-
'''
Created on 25 mai 2017

@author: tchenrezi
'''
from django.shortcuts import HttpResponseRedirect, render, redirect#, render, get_object_or_404, redirect, render_to_response,

from .forms import Produit_aliment_CreationForm, Produit_vegetal_CreationForm, Produit_objet_CreationForm, \
    Produit_service_CreationForm, ContactForm, AdresseForm, ProfilCreationForm, MessageForm, MessageGeneralForm, \
    ProducteurChangeForm, MessageGeneralCollectifsHLForm, Produit_aliment_modifier_form, Produit_service_modifier_form, \
    Produit_objet_modifier_form, Produit_vegetal_modifier_form, ChercherConversationForm, InscriptionNewsletterForm, \
    MessageChangeForm, ContactMailForm
from .models import Profil, Produit, Adresse, Choix, Panier, Item, get_categorie_from_subcat, Conversation, Message, \
    MessageGeneral, MessageGeneralCollectifsHL, getOrCreateConversation, Suivis, InscriptionNewsletter
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.core.mail import mail_admins, send_mail, BadHeaderError, send_mass_mail
from django_summernote.widgets import SummernoteWidget
from random import choice

from django import forms
from django.http import Http404

from blog.models import Article, Projet
#from jardinpartage.models import Article as Article_jardin

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import Group, User
from django.views.decorators.csrf import csrf_exempt

from django.views.decorators.debug import sensitive_variables
#from django.views.decorators.debug import sensitive_post_parameters

#from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, CharField
from django.db.models.functions import Lower
from django.utils.html import strip_tags

from actstream import actions, action
from actstream.models import Action, any_stream, following,followers
#from fcm_django.models import FCMDevice
# from django.http.response import JsonResponse, HttpResponse
# from django.views.decorators.http import require_GET, require_POST
# from django.shortcuts import get_object_or_404
# from django.contrib.auth.models import User
# from django.views.decorators.csrf import csrf_exempt
# from webpush import send_user_notification
# import json
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.exceptions import ObjectDoesNotExist
from marcheLibre.settings import SERVER_EMAIL

from django.utils.timezone import now

CharField.register_lookup(Lower, "lower")

#import sys
#from io import BytesIO
#from django.core.files.uploadedfile import InMemoryUploadedFile
#from PIL import Image
#from braces.views import LoginRequiredMixin

def handler404(request, *args, **kwargs):  #page not found
    response = render(request, "404.html")
    response.status_code = 404
    return response

def handler500(request, *args, **kwargs):   #erreur du serveur
    response = render(request, "500.html")
    response.status_code = 500
    return response

def handler403(request, *args, **kwargs):   #non autorisé
    response = render(request, "403.html")
    response.status_code = 403
    return response

def handler400(request, *args, **kwargs):   #requete invalide
    response = render(request, "400.html")
    response.status_code = 400
    return response


def tropGros(request):   #fichier trop gros
    response = render(request, "513.html")
    response.status_code = 513
    return response

def bienvenue(request):
    nums = ['01', '02', '03', '04', '07', '10', '11', '13', '15', '17', '20', '21', '23', ]
    nomImage = 'img/flo/resized0' +  choice(nums)+'.png'
    nbNotif = 0
    nbExpires = 0
    if request.user.is_authenticated:
        nbNotif = getNbNewNotifications(request)
        nbExpires = getNbProduits_expires(request)

    return render(request, 'bienvenue.html', {'nomImage':nomImage, "nbNotif": nbNotif , "nbExpires":nbExpires})


def presentation_site(request):
    return render(request, 'presentation_site.html')

def gallerie(request):
    return render(request, 'gallerie.html')

def faq(request):
    return render(request, 'faq.html')

def statuts(request):
    return render(request, 'statuts.html')

@login_required
def produit_proposer(request, type_produit):
    try:
        bgcolor = Choix.couleurs[type_produit]
    except:
        bgcolor = None

    if type_produit == 'aliment':
        type_form = Produit_aliment_CreationForm(request.POST or None, request.FILES or None)
    elif type_produit == 'vegetal':
        type_form = Produit_vegetal_CreationForm(request.POST or None, request.FILES or None)
    elif type_produit == 'service':
        type_form = Produit_service_CreationForm(request.POST or None, request.FILES or None)
    elif type_produit == 'objet':
        type_form = Produit_objet_CreationForm(request.POST or None, request.FILES or None)
    else:
        raise Exception('Type de produit inconnu (aliment, vegetal, service ou  objet)')

    if  type_form.is_valid():
       # produit = produit_form.save(commit=False)
        produit = type_form.save(commit=False)
        produit.user = request.user
        produit.categorie = type_produit

        if not request.user.is_collectifshl:
            produit.estPublique = True

        produit.save()
        url = produit.get_absolute_url()
        suffix = "" if produit.estPublique else "_collectifshl"
        offreOuDemande = "offre" if produit.estUneOffre else "demande"
        action.send(request.user, verb='ajout_offre'+suffix, action_object=produit, url=url,
                    description="a ajouté une "+offreOuDemande+" au marché : '%s'" %(produit.nom_produit))

        messages.info(request, 'Votre offre a été ajoutée !')
        return HttpResponseRedirect('/marcheLibre/detail/' + str(produit.id))
    return render(request, 'marcheLibre/produit_proposer.html', {"form": type_form, "bgcolor": bgcolor, "type_produit":type_produit})


class ProduitModifier(UpdateView):
    model = Produit
    template_name_suffix = '_modifier'
    fields = ['date_debut', 'date_expiration', 'nom_produit', 'description', 'prix', 'unite_prix', 'souscategorie', 'estUneOffre', 'estPublic', 'type_prix']# 'souscategorie','etat','type_prix']

    widgets = {
        'date_debut': forms.DateInput(attrs={'type': "date"}),
        'date_expiration': forms.DateInput(attrs={'type': "date"}),
        'description': SummernoteWidget(),
    }


    def get_form_class(self):
        if self.object.categorie == 'aliment':
            return Produit_aliment_modifier_form
        elif self.object.categorie == 'vegetal':
            return Produit_vegetal_modifier_form
        elif self.object.categorie == 'service':
            return Produit_service_modifier_form
        elif self.object.categorie == 'objet':
            return Produit_objet_modifier_form
        else:
            raise Exception('Type de produit inconnu (aliment, vegetal, service ou  objet)')
        return get_produitForm(self.request, self.object.categorie)

    def get_queryset(self):
        return self.model.objects.select_subclasses()

            # @login_required
class ProduitSupprimer(DeleteView):
    model = Produit
    success_url = reverse_lazy('marcheLibre')

@login_required
def proposerProduit_entree(request):
    return render(request, 'marcheLibre/produit_proposer_entree.html', {"couleurs":Choix.couleurs})


@login_required
def detailProduit(request, produit_id):
    try:
        prod = Produit.objects.get_subclass(id=produit_id)
    except ObjectDoesNotExist:
        raise Http404

    if not prod.estPublique and not request.user.is_collectifshl:
        return render(request, 'notMembre.html',)
    return render(request, 'marcheLibre/produit_detail.html', {'produit': prod})


def merci(request, template_name='merci.html'):
    return render(request, template_name)


@login_required
def profil_courant(request, ):
    nbExpires = getNbProduits_expires(request)
    return render(request, 'profil.html', {'user': request.user, "nbExpires":nbExpires})


@login_required
def profil(request, user_id):
    try:
        user = Profil.objects.get(id=user_id)
        distance = user.getDistance(request.user)
        return render(request, 'profil.html', {'user': user, 'distance':distance})
    except User.DoesNotExist:
            return render(request, 'profil_inconnu.html', {'userid': user_id})

@login_required
def profil_nom(request, user_username):
    try:
        user = Profil.objects.get(username=user_username)
        distance = user.getDistance(request.user)
        return render(request, 'profil.html', {'user': user, 'distance':distance})
    except User.DoesNotExist:
        return render(request, 'profil_inconnu.html', {'userid': user_username})

@login_required
def profil_inconnu(request):
    return render(request, 'profil_inconnu.html')

@login_required
def annuaire(request):
    profils = Profil.objects.filter(accepter_annuaire=True).order_by('username')
    nb_profils = len(Profil.objects.all())
    return render(request, 'annuaire.html', {'profils':profils, "nb_profils":nb_profils} )

@login_required
def annuaire_collectifshl(request):
    if not request.user.is_collectifshl:
        return render(request, "notMembre.html")

    profils_collectifshl = Profil.objects.filter(accepter_annuaire=True, statut_adhesion=2).order_by('username')
    nb_profils = len(Profil.objects.filter(statut_adhesion=2))
    return render(request, 'annuaire_collectifshl.html', {'profils':profils_collectifshl,"nb_profils": nb_profils } )

@login_required
def listeContacts(request):
    if not request.user.is_collectifshl:
        return render(request, "notMembre.html")
    listeMails = [
        {"type":'user_newsletter' ,"profils":Profil.objects.filter(inscrit_newsletter=True), "titre":"Liste des inscrits à la newsletter : "},
         {"type":'anonym_newsletter' ,"profils":InscriptionNewsletter.objects.all(), "titre":"Liste des inscrits anonymes à la newsletter : "},
      {"type":'user_adherent' , "profils":Profil.objects.filter(statut_adhesion=2), "titre":"Liste des adhérents : "},
        {"type":'user_futur_adherent', "profils":Profil.objects.filter(statut_adhesion=0), "titre":"Liste des personnes qui veulent adhérer à CollectifsHL :"}
    ]
    return render(request, 'listeContacts.html', {"listeMails":listeMails})

@login_required
def listeFollowers(request):
    if not request.user.is_collectifshl:
        return render(request, "notMembre.html")
    listeArticles = []
    for art in Article.objects.all():
        suiveurs = followers(art)
        if suiveurs:
            listeArticles.append({"titre": art.titre, "url": art.get_absolute_url(), "followers": suiveurs, })
    #for art in Article_jardin.objects.all():
        #suiveurs = followers(art)
        #if suiveurs:
            #listeArticles.append({"titre": art.titre, "url": art.get_absolute_url(), "followers": suiveurs, })
    for art in Projet.objects.all():
        suiveurs = followers(art)
        if suiveurs:
            listeArticles.append({"titre": art.titre, "url": art.get_absolute_url(), "followers": suiveurs, })

    return render(request, 'listeFollowers.html', {"listeArticles":listeArticles})

@login_required
def carte(request):
    profils = Profil.objects.filter(accepter_annuaire=1)
    return render(request, 'carte_cooperateurs.html', {'profils':profils, 'titre': "La carte des coopérateurs*" } )


@login_required
def admin_asso(request):
    if not request.user.is_collectifshl:
        return render(request, "notMembre.html")

    listeFichers = [
        {"titre": "Télécharger le bilan comptable", "url": "{{STATIC_ROOT]]/admin/coucou.txt"},
        {"titre":"Télécharger un RIB", "url":"{{STATIC_ROOT]]/admin/bilan.txt" },
        {"titre":"Télécharger les statuts et règlement intérieur", "url":"{{STATIC_ROOT]]/admin/statuts.txt" },
    ]
    return render(request, 'asso/admin_asso.html', {"listeFichers":listeFichers} )

def presentation_asso(request):
    return render(request, 'asso/presentation_asso.html')

@login_required
def telechargements_asso(request):
    if not request.user.is_collectifshl:
        return render(request, "notMembre.html")

    fichiers = [
        #{'titre' : 'Contrat credit mutuel', 'url': static('doc/contrat_credit_mutuel.pdf'),},

                ]
    return render(request, 'asso/fichiers.html', {'fichiers':fichiers})

@login_required
def adhesion_asso(request):
    return render(request, 'asso/adhesion.html', )

@login_required
def carte_collectifshl(request):
    if not request.user.is_collectifshl:
        return render(request, "notMembre.html")
    profils = Profil.objects.filter(statut_adhesion=2, accepter_annuaire=1)
    return render(request, 'carte_cooperateurs.html', {'profils':profils, 'titre': "Carte des adhérents CollectifsHL*" } )

@login_required
def profil_contact(request, user_id):
    recepteur = Profil.objects.get(id=user_id)
    if request.method == 'POST':
        form = ContactForm(request.POST or None, )
        if form.is_valid():
            sujet = "[collectifshl] "+ request.user.username + "(" + request.user.email+ ") vous a écrit: "+ form.cleaned_data['sujet']
            message_txt = ""
            message_html = form.cleaned_data['msg']
            recepteurs = [recepteur.email,]
            if form.cleaned_data['renvoi'] :
                recepteurs = [recepteur.email, request.user.email]

            send_mail(
                sujet,
                message_txt,
                request.user.email,
                recepteurs,
                html_message=message_html,
                fail_silently=False,
                )
            return render(request, 'contact/message_envoye.html', {'sujet': form.cleaned_data['sujet'], 'msg':message_html, 'envoyeur':request.user.username + " (" + request.user.email + ")", "destinataire":recepteur.username + " (" +recepteur.email+ ")"})
    else:
        form = ContactForm()
    return render(request, 'contact/profil_contact.html', {'form': form, 'recepteur':recepteur})

    #message = None
    #titre = None
    # id_panier = request.GET.get('panier')
    # if id_panier:
    #     panier = Panier.objects.get(id=id_panier)
    #     message = panier.get_message_demande(int(user_id))
    #     titre = "Proposition d'échange"
    #
    # id_produit = request.GET.get('produit')
    # if id_produit:
    #     produit = Produit.objects.get(id=id_produit)
    #     message = produit.get_message_demande()
    #     titre = "Au sujet de l'offre de " + produit.nom_produit


def contact_admins(request):
    if request.user.is_anonymous:
        form = ContactMailForm(request.POST or None, )
    else:
        form = ContactForm(request.POST or None, )

    if form.is_valid():

        if request.user.is_anonymous:
            envoyeur = "Anonyme : " + form.cleaned_data['email']
        else:
            envoyeur = request.user.username + " (" + request.user.email + ") "
        sujet = form.cleaned_data['sujet']
        message_txt = envoyeur + " a envoyé le message suivant : "
        message_html = form.cleaned_data['msg']
        try:
            mail_admins(sujet, message_txt, html_message=message_html)
            if form.cleaned_data['renvoi']:
                if request.user.is_anonymous:
                    send_mail(sujet, "Vous avez envoyé aux administrateurs du site www.CollectifsHLle message suivant : " + message_html, form.cleaned_data['email'], [form.cleaned_data['email'],], fail_silently=False, html_message=message_html)
                else:
                    send_mail(sujet, "Vous avez envoyé aux administrateurs du site www.CollectifsHLle message suivant : " + message_html, request.user.email, [request.user.email,], fail_silently=False, html_message=message_html)

            return render(request, 'contact/message_envoye.html', {'sujet': sujet, 'msg': message_html,
                                                   'envoyeur': envoyeur ,
                                                   "destinataire": "administrateurs "})
        except BadHeaderError:
            return render(request, 'erreur.html', {'msg':'Invalid header found.'})

        return render(request, 'erreur.html', {'msg':"Désolé, une ereur s'est produite"})

    return render(request, 'contact/contact.html', {'form': form, "isContactProducteur":False})





def contact_admins2(request):
    form = ContactForm(request.POST or None)
    if form.is_valid():
        if request.user.is_anonymous:
            envoyeur = "Anonyme"
        else:
            envoyeur = request.user.username + "(" + request.user.email + ") "
        sujet = form.cleaned_data['sujet']
        message = request.user.username + ' a envoyé le message suivant : \\n' + form.cleaned_data['message']
        mail_admins(sujet, message)
        if form.cleaned_data['renvoi'] :
            mess = "[CollectifsHL] message envoyé aux administrateurs : \\n"
            send_mail( sujet, mess + message, request.user.email, [request.user.email,], fail_silently=False,)
        return render(request, 'contact/message_envoye.html', {'sujet': sujet, 'message':message, 'envoyeur':request.user.username + "(" + request.uer.email + ")", "destinataire":"administrateurs d"
                                                                                                                                                                       "u site)"})
    return render(request, 'contact/contact.html', {'form': form, "isContactProducteur":False})


@login_required
def produitContacterProducteur(request, produit_id):
    prod = Produit.objects.get_subclass(pk=produit_id)
    receveur = prod.user
    form = ContactForm(request.POST or None)
    if form.is_valid():
        sujet =  "[CollectifsHL] " + request.user.username + "(" + request.user.email+ ") vous contacte au sujet de: "  + form.cleaned_data['sujet']
        message = form.cleaned_data['message'] + '(par : ' + request.username + ')'

        send_mail( sujet, message, request.user.email, receveur.email, fail_silently=False,)
        if form.cleaned_data['renvoi'] :
            mess = "[CollectifsHL] message envoyé à : "+receveur.email+"\\n"
            send_mail( sujet,mess + message, request.user.email, [request.user.email,], fail_silently=False,)

    return render(request, 'contact/contact.html', {'form': form, "isContactProducteur":True, "producteur":receveur.user.username})


@login_required
class profil_modifier_user(UpdateView):
    model = Profil
    form_class = ProducteurChangeForm
    template_name_suffix = '_modifier'
    fields = ['username', 'first_name', 'last_name', 'email', 'site_web', 'description', 'competences', 'pseudo_june', 'accepter_annuaire', 'inscrit_newsletter']

    def get_object(self):
        return Profil.objects.get(id=self.request.user.id)


class profil_modifier_adresse(UpdateView):
    model = Adresse
    form_class = AdresseForm
    template_name_suffix = '_modifier'
    

    def get_object(self):
        return Adresse.objects.get(id=self.request.user.id)

class profil_modifier(UpdateView):
    model = Profil
    form_class = ProducteurChangeForm
    template_name_suffix = '_modifier'
    #fields = ['username','email','first_name','last_name', 'site_web','description', 'competences', 'inscrit_newsletter']

    def get_object(self):
        return Profil.objects.get(id=self.request.user.id)

class profil_supprimer(DeleteView):
    model = Profil
    success_url = reverse_lazy('bienvenue')

    def get_object(self):
        return Profil.objects.get(id=self.request.user.id)

@sensitive_variables('password')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/password_changer_form.html', {
        'form': form
    })

@sensitive_variables('user', 'password1', 'password2')
def register(request):
    if request.user.is_authenticated:
        return render(request, "erreur.html", {"msg":"Vous etes déjà inscrit et authentifié !"})
    
    form_adresse = AdresseForm(request.POST or None)
    form_profil = ProfilCreationForm(request.POST or None)
    if form_adresse.is_valid() and form_profil.is_valid():
        adresse = form_adresse.save()
        profil_courant = form_profil.save(commit=False,is_active = False)
        profil_courant.adresse = adresse
        if profil_courant.statut_adhesion == 2:
            profil_courant.is_active=False
        profil_courant.save()
        Panier.objects.create(user=profil_courant)
        return render(request, 'userenattente.html')

    return render(request, 'register.html', {"form_adresse": form_adresse,"form_profil": form_profil,})


from datetime import date
class ListeProduit(ListView):
    model = Produit
    context_object_name = "produits_list"
    template_name = "produit_list.html"
    paginate_by = 30

    def get_qs(self):
        qs = Produit.objects.select_subclasses()
        if not self.request.user.is_authenticated or not self.request.user.is_collectifshl:
            qs = qs.filter(estPublique=True)
        params = dict(self.request.GET.items())

        if not "expire" in params:
            qs = qs.filter(Q(date_expiration__gt=date.today())| Q(date_expiration=None) )
        else:
            qs = qs.filter(Q(date_expiration__lt=date.today()) )

        
        if "distance" in params:
            listProducteurs = [p for p in Profil.objects.all() if p.getDistance(self.request.user) < float(params['distance'])] 
            qs = qs.filter(user__in=listProducteurs)

        if "producteur" in params:
            qs = qs.filter(user__username=params['producteur'])
        if "categorie" in params:
            qs = qs.filter(categorie=params['categorie'])
        if "souscategorie" in params:
            qs = qs.filter(Q(produit_aliment__souscategorie=params['souscategorie']) | Q(produit_vegetal__souscategorie=params['souscategorie']) | Q(produit_service__souscategorie=params['souscategorie'])  | Q(produit_objet__souscategorie=params['souscategorie']))

        if "prixmax" in params:
            qs = qs.filter(prix__lt=params['prixmax'])
        if "prixmin" in params:
            qs = qs.filter(prix__gtt=params['prixmin'])
        if "monnaie" in params:
            qs = qs.filter(unite_prix=params['monnaie'])
        if "gratuit" in params:
            qs = qs.filter(unite_prix='don')
        if "offre" in params:
            qs = qs.filter(estUneOffre=params['offre'])

        if "collectifshl" in params and self.request.user.is_collectifshl:
            if params['collectifshl'] == "True":
                qs = qs.filter(estPublique=False)
            else:
                qs = qs.filter(estPublique=True)

        res = qs.order_by('-date_creation', 'categorie', 'user')
        if "ordre" in params:
            if params['ordre'] == 'categorie':
                res = qs.order_by('categorie', '-date_creation', 'user')
            elif params['ordre'] == "producteur" :
                res = qs.order_by('user', '-date_creation', 'categorie', )
            elif params['ordre'] == "date":
                res = qs.order_by('-date_creation', 'categorie', 'user', )

        return res

    def get_queryset(self):
        return self.get_qs()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # context['producteur_list'] = Profil.objects.values_list('user__username', flat=True).distinct()
        context['choixPossibles'] = Choix.choix
        context['ordreTriPossibles'] = Choix.ordreTri
        context['distancePossibles'] = Choix.distances
        context['producteur_list'] = Profil.objects.all()
        context['typeFiltre'] = "aucun"
        # context['form'] = self.form
        if 'producteur' in self.request.GET:
            context['typeFiltre'] = "producteur"
        if 'souscategorie' in self.request.GET:
            categorie = get_categorie_from_subcat(self.request.GET['souscategorie'])
            context['categorie_parent'] = categorie
            context['typeFiltre'] = "souscategorie"
            context['souscategorie'] = self.request.GET['souscategorie']
        if 'categorie' in self.request.GET:
            context['categorie_parent'] = self.request.GET['categorie']
            context['typeFiltre'] = "categorie"
        context['typeOffre'] = '<- | ->'

        context['suivi'], created = Suivis.objects.get_or_create(nom_suivi="produits")
        return context

class ListeProduit_offres(ListeProduit):
    def get_queryset(self):
        qs = self.get_qs()
        qs = qs.filter(estUneOffre=True)
        return qs

    def get_context_data(self, **kwargs):
        context = ListeProduit.get_context_data(self, **kwargs)
        context['typeOffre'] = 'Offres->'
        return context

class ListeProduit_recherches(ListeProduit):
    def get_queryset(self):
        qs = self.get_qs()
        qs = qs.filter(estUneOffre=False)
        return qs

    def get_context_data(self, **kwargs):
        context = ListeProduit.get_context_data(self, **kwargs)
        context['typeOffre'] = '<-Demandes'
        return context

def charte(request):
    return render(request, 'asso/charte.html', )

def cgu(request):
    return render(request, 'cgu.html', )

@login_required
def liens(request):
    liens = [
        'https://www.hameaux-legers.org/',
        'https://www.balotilo.org/',
        'https://colibris-universite.org/mooc-permaculture/wakka.php?wiki=PagePrincipale',
        'https://www.monnaielibreoccitanie.org/',
        'http://lejeu.org/',
        'http://soudaqui.cat/wordpress/',
        'https://framasoft.org',
        'https://alternatiba.eu/alternatiba66/',
        'http://www.le-message.org/',
        'https://reporterre.net/',
        'https://la-bas.org/',
    ]
    return render(request, 'liens.html', {'liens':liens})

def fairedon(request):
    return render(request, 'fairedon.html', )

def agenda(request):
    return render(request, 'agenda.html', )


@login_required
def ajouterAuPanier(request, produit_id, quantite):#, **kwargs):
    quantite = float(quantite)
    produit = Produit.objects.get_subclass(pk=produit_id)
    # try:
    panier = Panier.objects.get(user=request.user, etat="a")
    # except ObjectDoesNotExist:
    #     profil = Profil.objects.get(user__id = request.user.id)
    #     panier = Panier(user=profil, )
    #     panier.save()
    panier.add(produit, produit.unite_prix, quantite)
    return afficher_panier(request)

@login_required
def enlever_du_panier(request, item_id):
    panier = Panier.objects.get(user=request.user, etat="a")
    panier.remove_item(item_id)
    return afficher_panier(request)


@login_required
def afficher_panier(request):
    # try:
    panier = Panier.objects.get(user=request.user, etat="a")
    # panier = get_object_or_404(Panier, user__id=profil_id, etat="a")
    # except ObjectDoesNotExist:
    #     profil = Profil.objects.get(user__id = request.user.id)
    #     panier = Panier(user=profil, )
    #     panier.save()
    items = Item.objects.order_by('produit__user').filter(panier__id=panier.id)
    return render(request, 'panier.html', {'panier':panier, 'items':items})


@login_required
def afficher_requetes(request):
    items = Item.objects.filter( produit__user__id =  request.user.id)
    return render(request, 'requetes.html', {'items':items})


@login_required
def chercher(request):
    recherche = str(request.GET.get('id_recherche')).lower()
    if recherche:
        from blog.models import Commentaire, CommentaireProjet
        produits_list = Produit.objects.filter(Q(description__icontains=recherche) | Q(nom_produit__lower__contains=recherche), ).select_subclasses()
        articles_list = Article.objects.filter(Q(titre__lower__contains=recherche) | Q(contenu__icontains=recherche), )
        projets_list = Projet.objects.filter(Q(titre__lower__contains=recherche) | Q(contenu__icontains=recherche), )
        profils_list = Profil.objects.filter(Q(username__lower__contains=recherche)  | Q(description__icontains=recherche)| Q(competences__icontains=recherche), )
        commentaires_list = Commentaire.objects.filter(Q(commentaire__icontains=recherche) )
        commentairesProjet_list = CommentaireProjet.objects.filter(Q(commentaire__icontains=recherche))
        salon_list = MessageGeneral.objects.filter(Q(message__icontains=recherche) )
    else:
        produits_list = []
        articles_list = []
        projets_list = []
        profils_list = []
        commentaires_list, commentairesProjet_list, salon_list = [],[],[]
    return render(request, 'chercher.html', {'recherche':recherche, 'articles_list':articles_list, 'produits_list':produits_list, "projets_list": projets_list, 'profils_list':profils_list,'commentaires_list': commentaires_list, 'commentairesProjet_list':commentairesProjet_list, 'salon_list':salon_list})


@login_required
def lireConversation(request, destinataire):
    conversation = getOrCreateConversation(request.user.username, destinataire)
    messages = Message.objects.filter(conversation=conversation).order_by("date_creation")

    message_defaut = None
    id_panier = request.GET.get('panier')
    if id_panier:
        id_destinataire = Profil.objects.get(username=destinataire).id
        message_defaut = Panier.objects.get(id=id_panier).get_message_demande(int(id_destinataire))

    id_produit = request.GET.get('produit')
    if id_produit:
        message_defaut = Produit.objects.get(id=id_produit).get_message_demande()

    form = MessageForm(request.POST or None, message=message_defaut)
    if form.is_valid():
        message = form.save(commit=False)
        message.conversation = conversation
        message.auteur = request.user
        conversation.date_dernierMessage = message.date_creation
        conversation.dernierMessage =  ("(" + str(message.auteur) + ") " + str(strip_tags(message.message).replace('&nspb',' ')))[:96] + "..."
        conversation.save()
        message.save()
        url = conversation.get_absolute_url()
        action.send(request.user, verb='envoi_salon_prive', action_object=conversation, url=url, group=destinataire,
                    description="a envoyé un message privé à " + destinataire)
        profil_destinataire = Profil.objects.get(username=destinataire)
        suivi, created = Suivis.objects.get_or_create(nom_suivi='conversations')
        if profil_destinataire in followers(suivi):
            sujet = "[CollectifsHL] quelqu'un vous a envoyé une message privé"
            message = request.user.username + " vous a envoyé un message privé. Vous pouvez y accéder en suivant ce lien : https://collectifshl.herokuapp.com" +  url
            try:
                send_mail(sujet, message, SERVER_EMAIL, [profil_destinataire.email, ], fail_silently=False,)
            except Exception as inst:
                mail_admins("erreur mails",
                        sujet + "\n" + message + "\n xxx \n" + str(profil_destinataire.email) + "\n erreur : " + str(inst))
        return redirect(request.path)

    return render(request, 'lireConversation.html', {'conversation': conversation, 'form': form, 'messages_echanges': messages, 'destinataire':destinataire})



@login_required
def lireConversation_2noms(request, destinataire1, destinataire2):
    if request.user.username==destinataire1:
        return lireConversation(request, destinataire2)
    elif request.user.username==destinataire2:
        return lireConversation(request, destinataire1)
    else:
        return render(request, 'erreur.html', {'msg':"Vous n'êtes pas autorisé à voir cette conversation"})


class ListeConversations(ListView):
    model = Conversation
    context_object_name = "conversation_list"
    template_name = "conversations.html"
    paginate_by = 1

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        context['suivis'], created = Suivis.objects.get_or_create(nom_suivi="conversations")
        context['convers'] = Conversation.objects.filter(Q(profil2__id=self.request.user.id) | Q(profil1__id=self.request.user.id)).order_by('-date_dernierMessage')

        return context

def chercherConversation(request):
    form = ChercherConversationForm(request.user, request.POST or None,)
    if form.is_valid():
        destinataire = (Profil.objects.all().order_by('username'))[int(form.cleaned_data['destinataire'])]
        return redirect('agora_conversation', destinataire=destinataire)
    else:
        return render(request, 'chercher_conversation.html', {'form': form})

@login_required
def getNotifications(request):
    if request.user.is_collectifshl:
        salons      = Action.objects.filter(Q(verb='envoi_salon') | Q(verb='envoi_salon_collectifshl'))[:30]
        articles    = Action.objects.filter(Q(verb='article_nouveau_collectifshl') | Q(verb='article_message_collectifshl')|
                                            Q(verb='article_nouveau') | Q(verb='article_message')| Q(verb='article_modifier')|
                                            Q(verb='article_modifier_collectifshl'))[:30]
        projets     = Action.objects.filter(Q(verb='projet_nouveau_collectifshl') | Q(verb='projet_message_collectifshl')|
                                            Q(verb='projet_nouveau') | Q(verb='projet_message')| Q(verb='projet_modifier')|
                                            Q(verb='projet_modifier_collectifshl'))[:30]
        offres      = Action.objects.filter(Q(verb='ajout_offre') | Q(verb='ajout_offre_collectifshl'))[:30]
        votations      = Action.objects.filter(Q(verb='ajout_votation') | Q(verb='ajout_votation_collectifshl'))[:30]
    else:
        salons      = Action.objects.filter(Q(verb='envoi_salon') | Q(verb='envoi_salon_collectifshl'))[:30]
        articles    = Action.objects.filter(Q(verb='article_nouveau') | Q(verb='article_message')| Q(verb='article_modifier'))[:30]
        projets     = Action.objects.filter(Q(verb='projet_nouveau') | Q(verb='projet_message')| Q(verb='projet_modifier'))[:30]
        offres      = Action.objects.filter(Q(verb='ajout_offre'))[:30]
        votations = []
    #fiches = Action.objects.filter(Q(verb='fiche_nouveau')|Q(verb='fiche_ajouter_atelier')|Q(verb='fiche_modifier')|Q(verb='fiche_atelier_modifier')|Q(verb='fiche_message'))[:30]
    fiches = Action.objects.filter(verb__startswith='fiche')[:30]
    ateliers = Action.objects.filter(Q(verb__startswith='atelier')|Q(verb=''))[:30]

    nbNotif = 10
    fiches = [art for i, art in enumerate(fiches) if i == 0 or not (art.description == fiches[i-1].description and art.actor == fiches[i-1].actor ) ][:nbNotif]
    ateliers = [art for i, art in enumerate(ateliers) if i == 0 or not (art.description == ateliers[i-1].description and art.actor == ateliers[i-1].actor ) ][:nbNotif]

    conversations = (any_stream(request.user).filter(Q(verb='envoi_salon_prive',)) | Action.objects.filter(Q(verb='envoi_salon_prive',  description="a envoyé un message privé à " + request.user.username) ))[:nbNotif]
    articles = [art for i, art in enumerate(articles) if i == 0 or not (art.description == articles[i-1].description  and art.actor == articles[i-1].actor)][:nbNotif]
    projets = [art for i, art in enumerate(projets) if i == 0 or not (art.description == projets[i-1].description and art.actor == projets[i-1].actor ) ][:nbNotif]
    salons = [art for i, art in enumerate(salons) if i == 0 or not (art.description == salons[i-1].description and art.actor == salons[i-1].actor ) ][:nbNotif]
    offres = [art for i, art in enumerate(offres) if i == 0 or not (art.description == offres[i-1].description and art.actor == offres[i-1].actor ) ][:nbNotif]
    inscription = Action.objects.filter(Q(verb='inscription') )

    return salons, articles, projets, offres, conversations, fiches, ateliers, inscription, votations

@login_required
def getNotificationsParDate(request):
    if request.user.is_collectifshl:
        actions      = Action.objects.filter( \
            Q(verb='envoi_salon') | Q(verb='envoi_salon_collectifshl')|Q(verb='article_nouveau_collectifshl') |
            Q(verb='article_message_collectifshl')|Q(verb='article_nouveau') | Q(verb='article_message')|
            Q(verb='article_modifier')| Q(verb='article_modifier_collectifshl')|Q(verb='projet_nouveau_collectifshl') |
            Q(verb='projet_message_collectifshl')|Q(verb='projet_nouveau') | Q(verb='projet_message')| Q(verb='projet_modifier')|
            Q(verb='projet_modifier_collectifshl')|Q(verb__startswith='fiche')|Q(verb__startswith='atelier')|
            Q(verb='envoi_salon_prive', description="a envoyé un message privé à " + request.user.username)|
            Q(verb='inscription') | Q(verb='votation_nouveau') \
        ).order_by('-timestamp')
    else:
        actions      = Action.objects.filter(Q(verb='envoi_salon') | Q(verb='envoi_salon_collectifshl')|
                                             Q(verb='article_nouveau') | Q(verb='article_message')|
                                             Q(verb='article_modifier')|Q(verb='projet_nouveau') |
                                             Q(verb='projet_message')| Q(verb='projet_modifier')|
                                             Q(verb='ajout_offre')|Q(verb__startswith='fiche')|
                                             Q(verb__startswith='atelier')|Q(verb='inscription') |
                                                Q(verb='envoi_salon_prive', description="a envoyé un message privé à " + request.user.username)
        ).order_by('-timestamp')

    actions = [art for i, art in enumerate(actions[:100]) if i == 0 or not (art.description == actions[i-1].description and art.actor == actions[i-1].actor ) ][:50]

    return actions

@login_required
def getNbNewNotifications(request):
    actions = getNotificationsParDate(request)
    actions = [action for action in actions if  request.user.date_notifications < action.timestamp]

    return len(actions)


@login_required
def get_notifications_news(request):
    actions = getNotificationsParDate(request)
    actions = [action for action in actions if  request.user.date_notifications < action.timestamp]
    return actions


@login_required
def notifications(request):
    salons, articles, projets, offres, conversations, fiches, ateliers, inscriptions, votations = getNotifications(request)
    return render(request, 'notifications/notifications.html', {'salons': salons, 'articles': articles,'projets': projets, 'offres':offres, 'conversations':conversations, 'fiches':fiches, 'ateliers':ateliers, 'inscriptions':inscriptions, 'votations':votations})

@login_required
def notifications_news(request):
    actions = get_notifications_news(request)
    return render(request, 'notifications/notifications_last.html', {'actions':actions})


@login_required
def notificationsParDate(request):
    actions = getNotificationsParDate(request)
    return render(request, 'notifications/notificationsParDate.html', {'actions': actions, })

@login_required
def notificationsLues(request):
    request.user.date_notifications = now()
    request.user.save()
    return redirect('notifications_news')

def getInfosJourPrecedent(request, nombreDeJours):
    from datetime import datetime, timedelta
    timestamp_from = datetime.now().date() - timedelta(days=nombreDeJours)
    timestamp_to = datetime.now().date() - timedelta(days=nombreDeJours - 1)

    if request.user.is_collectifshl:
        articles    = Action.objects.filter(Q(verb='article_nouveau_collectifshl', timestamp__gte = timestamp_from,timestamp__lte = timestamp_to,) | Q(verb='article_nouveau',timestamp__gte = timestamp_from, timestamp__lte = timestamp_to,))
        projets     = Action.objects.filter(Q(verb='projet_nouveau_collectifshl', timestamp__gte = timestamp_from,timestamp__lte = timestamp_to,) |Q(verb='projet_nouveau', timestamp__gte = timestamp_from,timestamp__lte = timestamp_to,))
        offres      = Action.objects.filter(Q(verb='ajout_offre', timestamp__gte = timestamp_from,timestamp__lte = timestamp_to,) | Q(verb='ajout_offre_collectifshl', timestamp__gte = timestamp_from,timestamp__lte = timestamp_to,))
    else:
        articles    = Action.objects.filter(Q(verb='article_nouveau', timestamp__gte = timestamp_from, timestamp__lte = timestamp_to,) | Q(verb='article_modifier', timestamp__gte = timestamp_from,timestamp__lte = timestamp_to,))
        projets     = Action.objects.filter(Q(verb='projet_nouveau', timestamp__gte = timestamp_from,timestamp__lte = timestamp_to,))
        offres      = Action.objects.filter(Q(verb='ajout_offre', timestamp__gte = timestamp_from,timestamp__lte = timestamp_to,))
    fiches = Action.objects.filter(verb__startswith='fiche')
    ateliers = Action.objects.filter(Q(verb__startswith='atelier')|Q(verb=''))
    conversations = (any_stream(request.user).filter(Q(verb='envoi_salon_prive', )) | Action.objects.filter(
        Q(verb='envoi_salon_prive', description="a envoyé un message privé à " + request.user.username)))

    articles = [art for i, art in enumerate(articles) if i == 0 or not (art.description == articles[i-1].description  and art.actor == articles[i-1].actor)]
    projets = [art for i, art in enumerate(projets) if i == 0 or not (art.description == projets[i-1].description and art.actor == projets[i-1].actor) ]
    offres = [art for i, art in enumerate(offres) if i == 0 or not (art.description == offres[i-1].description and art.actor == offres[i-1].actor) ]
    fiches = [art for i, art in enumerate(fiches) if i == 0 or not (art.description == fiches[i-1].description and art.actor == fiches[i-1].actor ) ]
    ateliers = [art for i, art in enumerate(ateliers) if i == 0 or not (art.description == ateliers[i-1].description and art.actor == ateliers[i-1].actor ) ]
    conversations = [art for i, art in enumerate(conversations) if i == 0 or not (art.description == conversations[i-1].description and art.actor == conversations[i-1].actor ) ]

    return articles, projets, offres, fiches, ateliers, conversations

def getTexteJourPrecedent(nombreDeJour):
    if nombreDeJour == 0:
        return "Aujourd'hui"
    elif nombreDeJour == 1:
        return "Hier"
    elif nombreDeJour == 2:
        return "Avant-hier"
    else:
        return "Il y a " + str(nombreDeJour) + " jours"

@login_required
def dernieresInfos(request):
    info_parjour = []
    for i in range(15):
        info_parjour.append({"jour":getTexteJourPrecedent(i), "infos":getInfosJourPrecedent(request, i)})
    return render(request, 'notifications/notifications_news.html', {'info_parjour': info_parjour,})


@login_required
def getNbProduits_expires(request):
    return len(Produit.objects.filter(user=request.user, date_expiration__lt=date.today()))


@login_required
def supprimerProduits_expires_confirmation(request):

    qs = Produit.objects.select_subclasses()
    produits = qs.filter(user=request.user, date_expiration__lt=date.today())
    return render(request, 'marcheLibre/produitexpires_confirm_delete.html', {'produits': produits,})

@login_required
def supprimerProduits_expires(request):
    produits = Produit.objects.filter(user=request.user, date_expiration__lt=date.today())

    for prod in produits:
        prod.delete()

    return redirect('bienvenue')


@login_required
def prochaines_rencontres(request):
    return render(request, 'notifications/prochaines_rencontres.html', {})



@login_required
def mesSuivis(request):
    actions = following(request.user)
    return render(request, 'notifications/mesSuivis.html', {'actions': actions, })


@login_required
def agora(request, ):
    messages = MessageGeneral.objects.all().order_by("date_creation")
    form = MessageGeneralForm(request.POST or None) 
    if form.is_valid(): 
        message = form.save(commit=False) 
        message.auteur = request.user 
        message.save()
        group, created = Group.objects.get_or_create(name='tous')
        url = reverse('agora_general')
        action.send(request.user, verb='envoi_salon', action_object=message, target=group, url=url, description="a envoyé un message dans le salon public")
        return redirect(request.path) 
    return render(request, 'agora.html', {'form': form, 'messages_echanges': messages})

@login_required
def agora_collectifshl(request, ):
    if not request.user.is_collectifshl:
        return render(request, "notMembre.html")
    messages = MessageGeneralCollectifsHL.objects.all().order_by("date_creation")
    form = MessageGeneralCollectifsHLForm(request.POST or None)
    if form.is_valid():
        message = form.save(commit=False)
        message.auteur = request.user

        message.save()
        group, created = Group.objects.get_or_create(name='collectifshl')
        url = reverse('agora_collectifshl')
        action.send(request.user, verb='envoi_salon_collectifshl', action_object=message, target=group, url=url,
                    description="a envoyé un message dans le salon CollectifsHL")


        return redirect(request.path)
    return render(request, 'agora_collectifshl.html', {'form': form, 'messages_echanges': messages})



# class ServiceWorkerView(View):
#     def get(self, request, *args, **kwargs):
#         return render(request, 'fcmtest/firebase-messaging-sw.js', content_type="application/x-javascript")
#
# @require_POST
# @csrf_exempt
# def send_push(request):
#     try:
#         body = request.body
#         data = json.loads(body)
#
#         if 'head' not in data or 'body' not in data or 'id' not in data:
#             return JsonResponse(status=400, data={"message": "Invalid data format"})
#
#         user_id = data['id']
#         user = get_object_or_404(User, pk=user_id)
#         payload = {'head': data['head'], 'body': data['body']}
#         send_user_notification(user=user, payload=payload, ttl=1000)
#
#         return JsonResponse(status=200, data={"message": "Web push successful"})
#     except TypeError:
#         return JsonResponse(status=500, data={"message": "An error occurred"})


@login_required
@csrf_exempt
def suivre_conversations(request, actor_only=True):
    """
    """
    suivi, created = Suivis.objects.get_or_create(nom_suivi='conversations')
    if suivi in following(request.user):
        actions.unfollow(request.user, suivi)
    else:
        actions.follow(request.user, suivi, actor_only=actor_only)
    return redirect('conversations')

@login_required
@csrf_exempt
def suivre_produits(request, actor_only=True):
    suivi, created = Suivis.objects.get_or_create(nom_suivi='produits')

    if suivi in following(request.user):
        actions.unfollow(request.user, suivi)
    else:
        actions.follow(request.user, suivi, actor_only=actor_only)
    return redirect('marcheLibre')




def inscription_newsletter(request):
    form = InscriptionNewsletterForm(request.POST or None)
    if form.is_valid():
        inscription = form.save(commit=False)
        inscription.save()
        return render(request, 'merci.html', {'msg' :"Vous êtes inscrits à la newsletter"})
    return render(request, 'registration/inscription_newsletter.html', {'form':form})


@login_required
def contacter_newsletter(request):
    if not request.user.is_collectifshl:
        return render(request, "notMembre.html")

    if request.method == 'POST':
        form = ContactForm(request.POST or None, )
        if form.is_valid():
            sujet = "[collectifshl] Newsletter - " +  form.cleaned_data['sujet']
            message = form.cleaned_data['msg']
            emails = [profil.email for profil in Profil.objects.filter(inscrit_newsletter=True)] + [profil.email for
                                                                                                    profil in
                                                                                                    InscriptionNewsletter.objects.all()]

            try:
                send_mass_mail([(sujet, message, SERVER_EMAIL, emails), ])
            except:
                sujet = "[collectifshl admin] Erreur lors de l'envoi du mail"
                message_txt = message + '\n'.join(emails)

                try:
                    mail_admins(sujet, message_txt)
                except:
                    print("erreur de la fonction contacterNewsletter (views.py)")
                    pass
            return render(request, 'contact/message_envoye.html', {'sujet': form.cleaned_data['sujet'], 'msg': message,
                                                           'envoyeur': request.user.username + " (" + request.user.email + ")",
                                                           "destinataires": emails})
    else:
        form = ContactForm()
    return render(request, 'contact/contact_newsletter.html', {'form': form, })



@login_required
def contacter_adherents(request):
    if not request.user.is_collectifshl:
        return render(request, "notMembre.html")

    if request.method == 'POST':
        form = ContactForm(request.POST or None, )
        if form.is_valid():
            sujet = "[collectifshl] Newsletter - " +  form.cleaned_data['sujet']
            message = form.cleaned_data['msg']
            emails = [profil.email for profil in Profil.objects.filter(statut_adhesion=2)]

            try:
                send_mass_mail([(sujet, message, SERVER_EMAIL, emails), ])
            except:
                sujet = "[collectifshl admin] Erreur lors de l'envoi du mail"
                message_txt = message + '\n'.join(emails)

                try:
                    mail_admins(sujet, message_txt)
                except:
                    print("erreur de la fonction contacterAdherents (views.py)")
                    pass
            return render(request, 'contact/message_envoye.html', {'sujet': form.cleaned_data['sujet'], 'msg': message,
                                                           'envoyeur': request.user.username + " (" + request.user.email + ")",
                                                           "destinataires": emails})
    else:
        form = ContactForm()
    return render(request, 'contact/contact_adherents.html', {'form': form, })



@login_required
def modifier_message(request, id, type):
    if type == 'general':
        obj = MessageGeneral.objects.get(id=id)
    elif type == 'collectifshl':
        if not request.user.is_collectifshl:
            return render(request, "notCollectifsHL")
        obj = MessageGeneralCollectifsHL.objects.get(id=id)



    elif type == 'conversation':
        obj = Message.objects.get(id=id)
    else:
        return render(request, 'erreur.html', {'msg':"Le salon que vous cherchez n'existe pas, désolé."})


    form = MessageChangeForm(request.POST or None, instance=obj)

    if form.is_valid():
        object = form.save()
        if object.message and object.message !='<br>':
            object.date_modification = now()
            object.save()
            return redirect (object.get_absolute_url)
        else:
            object.delete()
            return reverse('agora_general')


    return render(request, 'modifierCommentaire.html', {'form': form, })

