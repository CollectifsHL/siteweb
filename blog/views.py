# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect, reverse
from django.urls import reverse_lazy
from django.utils.html import strip_tags
from .models import Article, Commentaire, Projet, CommentaireProjet, Choix, Evenement
from .forms import ArticleForm, CommentaireArticleForm, CommentaireArticleChangeForm, ArticleChangeForm, ProjetForm, \
    ProjetChangeForm, CommentProjetForm, CommentaireProjetChangeForm, EvenementForm, EvenementArticleForm
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, UpdateView, DeleteView
from actstream import actions, action
from actstream.models import followers, following, action_object_stream, actor_stream
from django.core.mail import send_mass_mail, mail_admins
from django.utils.timezone import now
from marcheLibre.settings import SERVER_EMAIL

#from django.contrib.contenttypes.models import ContentType
from marcheLibre.models import Suivis
from django.views.decorators.csrf import csrf_exempt
import sys

# @login_required
# def forum(request):
#     """ Afficher tous les articles de notre blog """
#     articles = Article.objects.all().order_by('-date_dernierMessage')  # Nous sélectionnons tous nos articles
#     return render(request, 'blog/forum.html', {'derniers_articles': articles })

def accueil(request):
    return render(request, 'blog/accueil.html')


@login_required
def ajouterArticle(request):
    try:
        form = ArticleForm(request.POST or None)
        if form.is_valid():
            article = form.save(request.user)
            url = article.get_absolute_url()
            suffix = "" if article.estPublic else "_collectifshl"
            action.send(request.user, verb='article_nouveau'+suffix, action_object=article, url=url,
                        description="a ajouté un article : '%s'" % article.titre)
            return redirect(article.get_absolute_url())
            #return render(request, 'blog/lireArticle.html', {'article': article})
    except Exception as inst:
        print(inst)
    return render(request, 'blog/ajouterPost.html', { "form": form, })


# @login_required
class ModifierArticle(UpdateView):
    model = Article
    form_class = ArticleChangeForm
    template_name_suffix = '_modifier'
#    fields = ['user','site_web','description', 'competences', 'adresse', 'avatar', 'inscrit_newsletter']

    def get_object(self):
        return Article.objects.get(slug=self.kwargs['slug'])

    def form_valid(self, form):
        self.object = form.save()
        self.object.date_modification = now()
        self.object.save(sendMail=False)
        url = self.object.get_absolute_url()
        suffix = "_collectifshl" if not self.object.estPublic else ""
        action.send(self.request.user, verb='article_modifier'+suffix, action_object=self.object, url=url,
                     description="a modifié l'article: '%s'" % self.object.titre)
        #envoi_emails_articleouprojet_modifie(self.object, "L'article " +  self.object.titre + "a été modifié", True)
        return HttpResponseRedirect(self.get_success_url())


class SupprimerArticle(DeleteView):
    model = Article
    success_url = reverse_lazy('blog:index')
    template_name_suffix = '_supprimer'
#    fields = ['user','site_web','description', 'competences', 'adresse', 'avatar', 'inscrit_newsletter']

    def get_object(self):
        return Article.objects.get(slug=self.kwargs['slug'])



@login_required
def lireArticle(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if not article.estPublic and not request.user.is_collectifshl:
        return render(request, 'notMembre.html',)

    commentaires = Commentaire.objects.filter(article=article).order_by("date_creation")
    dates = Evenement.objects.filter(article=article).order_by("start_time")

    actions = action_object_stream(article)

    form = CommentaireArticleForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        if comment:
            comment.article = article
            comment.auteur_comm = request.user
            article.date_dernierMessage = comment.date_creation if comment.date_creation else now()
            article.dernierMessage = ("(" + str(comment.auteur_comm) + ") " + str(strip_tags(comment.commentaire).replace('&nspb',' ')))[:96] + "..."
            article.save(sendMail=False)
            comment.save()
            url = article.get_absolute_url()+"#idConversation"
            suffix = "_collectifshl" if not article.estPublic else ""
            action.send(request.user, verb='article_message'+suffix, action_object=article, url=url,
                        description="a réagi à l'article: '%s'" % article.titre)
            #envoi_emails_articleouprojet_modifie(article, request.user.username + " a réagit au projet: " +  article.titre, True)
        return redirect(request.path)

    return render(request, 'blog/lireArticle.html', {'article': article, 'form': form, 'commentaires':commentaires, 'dates':dates, 'actions':actions},)

@login_required
def lireArticle_id(request, id):
    article = get_object_or_404(Article, id=id)
    return lireArticle(request, slug=article.slug)


class ListeArticles(ListView):
    model = Article
    context_object_name = "article_list"
    template_name = "blog/index.html"
    paginate_by = 30

    def get_queryset(self):
        params = dict(self.request.GET.items())

        if "archives" in params and params['archives']:
            qs = Article.objects.filter(estArchive=True)
        else:
            qs = Article.objects.filter(estArchive=False)

        if not self.request.user.is_authenticated or not self.request.user.is_collectifshl:
            qs = qs.filter(estPublic=True)

        if "auteur" in params:
            qs = qs.filter(auteur__username=params['auteur'])
        if "categorie" in params:
            qs = qs.filter(categorie=params['categorie'])
        if "collectifshl" in params  and self.request.user.is_collectifshl:
            if params['collectifshl'] == "True":
                qs = qs.filter(estPublic=False)
            else:
                qs = qs.filter(estPublic=True)

        if "ordreTri" in params:
            qs = qs.order_by(params['ordreTri'])
        else:
            qs = qs.order_by('-date_dernierMessage', '-date_creation', 'categorie', 'auteur')

        return qs

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # context['producteur_list'] = Profil.objects.values_list('username', flat=True).distinct()
        context['auteur_list'] = Article.objects.order_by('auteur').values_list('auteur__username', flat=True).distinct()
        cat= Article.objects.order_by('categorie').values_list('categorie', flat=True).distinct()
        context['categorie_list'] = [(x[0], x[1], Choix.get_couleur(x[0])) for x in Choix.type_annonce if x[0] in cat]
        context['typeFiltre'] = "aucun"
        context['suivis'], created = Suivis.objects.get_or_create(nom_suivi="articles")

        context['ordreTriPossibles'] = {
                                           "date de création":'-date_creation',
                                           "date du dernier message":'-date_dernierMessage',
                                           "date de la dernière modification":'-date_modification',
                                            "titre": 'titre' }

        if 'auteur' in self.request.GET:
            context['typeFiltre'] = "auteur"
        if 'categorie' in self.request.GET:
            context['typeFiltre'] = "categorie"
            try:
                context['categorie_courante'] = [x[1] for x in Choix.type_annonce if x[0] == self.request.GET['categorie']][0]
            except:
                context['categorie_courante'] = ""
        if 'collectifshl' in self.request.GET:
            context['typeFiltre'] = "collectifshl"
        if 'archives' in self.request.GET:
            context['typeFiltre'] = "archives"
        if 'ordreTri' in self.request.GET:
            context['typeFiltre'] = "ordreTri"
        return context



# @login_required
# def ajouterNouveauProjet(request):
#     ModelFormWithFileField
#         if form.is_valid():
#             #simple_upload(request, 'fichier_projet')
#             projet = form.save(request.user)
#             return render(request, 'blog/lireProjet.html', {'projet': projet})
#         return render(request, 'blog/ajouterProjet.html', { "form": form, })

@login_required
def ajouterNouveauProjet(request):
    if request.method == 'POST':
        form = ProjetForm(request.POST, request.FILES)
        if form.is_valid():
            # file is saved
            projet = form.save(request.user)
            url = projet.get_absolute_url()

            suffix = "" if projet.estPublic else "_collectifshl"
            action.send(request.user, verb='projet_nouveau'+suffix, action_object=projet, url=url,
                    description="a ajouté un projet : '%s'" % projet.titre)
            return redirect(url)

    else:
        form = ProjetForm(request.POST or None, request.FILES or None)
    return render(request, 'blog/ajouterProjet.html', { "form": form, })

class ModifierProjet(UpdateView):
    model = Projet
    form_class = ProjetChangeForm
    template_name_suffix = '_modifier'
    #fields = ['user','site_web','description', 'competences', 'adresse', 'avatar', 'inscrit_newsletter']

    def get_object(self):
        return Projet.objects.get(slug=self.kwargs['slug'])

    def form_valid(self, form):
        self.object = form.save()
        self.object.date_modification = now()
        self.object.save()
        url = self.object.get_absolute_url()
        suffix = "_collectifshl" if not self.object.estPublic else ""
        action.send(self.request.user, verb='projet_modifier'+suffix, action_object=self.object, url=url,
                     description="a modifié le projet: '%s'" % self.object.titre)
        #envoi_emails_articleouprojet_modifie(self.object, "Le projet " +  self.object.titre + "a été modifié", False)
        return HttpResponseRedirect(self.get_success_url())

class SupprimerProjet(DeleteView):
    model = Projet
    success_url = reverse_lazy('blog:index_projets')
    template_name_suffix = '_supprimer'
#    fields = ['user','site_web','description', 'competences', 'adresse', 'avatar', 'inscrit_newsletter']

    def get_object(self):
        return Projet.objects.get(slug=self.kwargs['slug'])

@login_required
def lireProjet(request, slug):
    projet = get_object_or_404(Projet, slug=slug)

    if not projet.estPublic and not request.user.is_collectifshl:
        return render(request, 'notMembre.html',)

    commentaires = CommentaireProjet.objects.filter(projet=projet).order_by("date_creation")
    actions = action_object_stream(projet)

    form = CommentProjetForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.projet = projet
        comment.auteur_comm = request.user
        projet.date_dernierMessage = comment.date_creation
        projet.dernierMessage = ("(" + str(comment.auteur_comm) + ") " + str(strip_tags(comment.commentaire).replace('&nspb',' ')))[:96] + "..."
        projet.save(sendMail=False)
        comment.save()
        url = projet.get_absolute_url()+"#idConversation"
        suffix = "_collectifshl" if not projet.estPublic else ""
        action.send(request.user, verb='projet_message'+suffix, action_object=projet, url=url,
                    description="a réagit au projet: '%s'" % projet.titre)
        #envoi_emails_articleouprojet_modifie(projet, request.user.username + " a réagit au projet: " +  projet.titre, False)
        return redirect(request.path)

    return render(request, 'blog/lireProjet.html', {'projet': projet, 'form': form, 'commentaires':commentaires, 'actions':actions},)

def envoi_emails_articleouprojet_modifie(articleOuProjet, message, flag_article):

    titre = "[CollectifsHL] Article actualisé" if flag_article else "[CollectifsHL] Projet actualisé"
    message =  message +\
              "\n Vous pouvez y accéder en suivant ce lien : http://collectifshl.herokuapp.com" + articleOuProjet.get_absolute_url() + \
              "\n\n------------------------------------------------------------------------------" \
              "\n Pour vous désabonner cliquez sur la cloche sur http://collectifshl.herokuapp.com/forum/articles/" if flag_article else "\n Pour vous désabonner cliquez sur la cloche sur http://collectifshl.herokuapp.com/forum/projets/"
   # emails = [(titre, message, SERVER_EMAIL, (suiv.email, )) for suiv in followers(instance)]
    emails = [suiv.email for suiv in followers(articleOuProjet)  if articleOuProjet.auteur != suiv  and (articleOuProjet.estPublic or suiv.is_collectifshl)]

    if emails:
        try:
            send_mass_mail([(titre, message, SERVER_EMAIL, emails), ])
            #mail_admins("pas d'erreur mails", titre + "\n" + message + "\n xxx \n" + str(emails))
        except:
            mail_admins("erreur", sys.exc_info()[0])


class ListeProjets(ListView):
    model = Projet
    context_object_name = "projet_list"
    template_name = "blog/index_projets.html"
    paginate_by = 30

    def get_queryset(self):

        params = dict(self.request.GET.items())

        if "archives" in params and params['archives']:
            qs = Projet.objects.filter(estArchive=True)
        else:
            qs = Projet.objects.filter(estArchive=False)

        if not self.request.user.is_authenticated or not self.request.user.is_collectifshl:
            qs = qs.filter(estPublic=True)

        if "auteur" in params:
            qs = qs.filter(auteur__username=params['auteur'])
        if "categorie" in params:
            qs = qs.filter(categorie=params['categorie'])
        if "collectifshl" in params and self.request.user.is_collectifshl:
            if params['collectifshl'] == "True":
                qs = qs.filter(estPublic=False)
            else:
                qs = qs.filter(estPublic=True)

        if "ordreTri" in params:
            qs = qs.order_by(params['ordreTri'])
        else:
            qs = qs.order_by('-date_dernierMessage', '-date_creation', 'categorie', 'auteur')

        return qs

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # context['producteur_list'] = Profil.objects.values_list('username', flat=True).distinct()
        context['auteur_list'] = Projet.objects.order_by('auteur').values_list('auteur__username', flat=True).distinct()
        cat = Projet.objects.order_by('categorie').values_list('categorie', flat=True).distinct()
        context['categorie_list'] = [x for x in Choix.type_projet if x[0] in cat]
        context['typeFiltre'] = "aucun"

        context['ordreTriPossibles'] = ['-date_creation', '-date_dernierMessage', 'categorie', 'auteur', 'titre']
        if 'auteur_id' in self.request.GET:
            context['typeFiltre'] = "auteur"
        if 'categorie' in self.request.GET:
            context['typeFiltre'] = "categorie"
            try:
                context['categorie_courante'] = [x[1] for x in Choix.type_projet if x[0] == self.request.GET['categorie']][0]
            except:
                context['categorie_courante'] = ""
        if 'collectifshl' in self.request.GET:
            context['typeFiltre'] = "collectifshl"
        if 'archives' in self.request.GET:
            context['typeFiltre'] = "archives"
        if 'ordreTri' in self.request.GET:
            context['typeFiltre'] = "ordreTri"
        context['suivis'], created = Suivis.objects.get_or_create(nom_suivi="projets")
        return context


# from django.shortcuts import render
# from django.conf import settings
# from django.core.files.storage import FileSystemStorage
#
# def simple_upload(request, nomfichier):
#     if request.method == 'POST' and request.FILES[nomfichier]:
#         myfile = request.FILES[nomfichier]
#         fs = FileSystemStorage()
#         file_path = os.path.join(settings.MEDIA_ROOT, myfile.name)
#         filename = fs.save(file_path, myfile)
#         uploaded_file_url = fs.url(filename)
#         return render(request, 'simple_upload.html', {'uploaded_file_url': uploaded_file_url})
#     return render(request, 'simple_upload.html')


import os
from django.http import HttpResponse, Http404
from django.conf import settings


@login_required
def telecharger_fichier(request):
    path = request.GET['path']
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        mess = "fichier OK"
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read())
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    else:
        mess = "Fichier introuvable"
    return render(request, 'blog/telechargement.html', {'fichier':file_path, 'message': mess})

#
# def upload(request):
#     if request.POST:
#         form = FileForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return render_to_response('project/upload_successful.html')
#     else:
#         form = FileForm()
#     args = {}
#     args.update(csrf(request))
#     args['form'] = form
#
#     return render_to_response('project/create.html', args)


@login_required
@csrf_exempt
def suivre_projet(request, slug, actor_only=True):
    """
    """
    projet = get_object_or_404(Projet, slug=slug)

    if projet in following(request.user):
        actions.unfollow(request.user, projet)
    else:
        actions.follow(request.user, projet, actor_only=actor_only)
    return redirect(projet)


@login_required
@csrf_exempt
def suivre_article(request, slug, actor_only=True):
    """
    """
    article = get_object_or_404(Article, slug=slug)

    if article in following(request.user):
        actions.unfollow(request.user, article)
    else:
        actions.follow(request.user, article, actor_only=actor_only)
    return redirect(article)


@login_required
def projets_suivis(request, slug):
    projet = Projet.objects.get(slug=slug)
    suiveurs = followers(projet)
    return render(request, "blog/projets_suivis.html", {'suiveurs': suiveurs, "projet":projet})

@login_required
def articles_suivis(request, slug):
    article = Article.objects.get(slug=slug)
    suiveurs = followers(article)
    return render(request, 'blog/articles_suivis.html', {'suiveurs': suiveurs, "article":article, })

@login_required
def articles_suiveurs(request):
    suivi, created = Suivis.objects.get_or_create(nom_suivi = 'articles')
    suiveurs = followers(suivi)
    return render(request, 'blog/articles_suivis.html', {'suiveurs': suiveurs, })


@login_required
@csrf_exempt
def suivre_articles(request, actor_only=True):
    suivi, created = Suivis.objects.get_or_create(nom_suivi = 'articles')

    if suivi in following(request.user):
        actions.unfollow(request.user, suivi)
    else:
        actions.follow(request.user, suivi, actor_only=actor_only)
    return redirect('blog:index')

@login_required
@csrf_exempt
def suivre_projets(request, actor_only=True):
    suivi, created = Suivis.objects.get_or_create(nom_suivi = 'projets')

    if suivi in following(request.user):
        actions.unfollow(request.user, suivi)
    else:
        actions.follow(request.user, suivi, actor_only=actor_only)
    return redirect('blog:index_projets')



class ModifierCommentaireArticle(UpdateView):
    model = Commentaire
    form_class = CommentaireArticleChangeForm
    template_name = 'modifierCommentaire.html'

    def get_object(self):
        return Commentaire.objects.get(id=self.kwargs['id'])

    def form_valid(self, form):
        self.object = form.save()
        if self.object.commentaire and self.object.commentaire !='<br>':
            self.object.date_modification = now()
            self.object.save()
        else:
            self.object.delete()
        return HttpResponseRedirect(self.object.article.get_absolute_url())


class ModifierCommentaireProjet(UpdateView):
    model = CommentaireProjet
    form_class = CommentaireProjetChangeForm
    template_name = 'modifierCommentaire.html'

    def get_object(self):
        return CommentaireProjet.objects.get(id=self.kwargs['id'])

    def form_valid(self, form):
        self.object = form.save()
        if self.object.commentaire and self.object.commentaire !='<br>':
            self.object.date_modification = now()
            self.object.save()
        else:
            self.object.delete()
        return HttpResponseRedirect(self.object.projet.get_absolute_url())


@login_required
def ajouterEvenement(request, date=None):
    if date:
        form = EvenementForm(request.POST or None, initial={'start_time': date})
    else:
        form = EvenementForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('cal:agenda')

    return render(request, 'blog/ajouterEvenement.html', {'form': form, })



@login_required
def ajouterEvenementArticle(request, id):
    form = EvenementArticleForm(request.POST or None)

    if form.is_valid():
        form.save(id)
        return lireArticle_id(request, id)

    return render(request, 'blog/ajouterEvenement.html', {'form': form, })


# def changerArticles_jardin(request):
#     from jardinpartage.models import Article as Art_jardin, Commentaire as Comm_jardin
#     articles = Article.objects.filter(categorie="Jardin")
#     for article in articles:
#         new_art = Art_jardin.objects.create(categorie='Discu',
#                                 titre = article.titre,
#                                 auteur = article.auteur,
#                                 slug = article.slug,
#                                 contenu = article.contenu,
#                                 date_creation = article.date_creation,
#                                 date_modification = article.date_modification,
#                                 estPublic = article.estPublic,
#                                 estModifiable = article.estModifiable,
#
#                                 date_dernierMessage = article.date_dernierMessage,
#                                 dernierMessage = article.dernierMessage,
#                                 estArchive = article.estArchive,)
#         commentaires = Commentaire.objects.filter(article=article)
#         for commentaire in commentaires:
#             new = Comm_jardin.objects.create(auteur_comm = commentaire.auteur_comm, commentaire = commentaire.commentaire,
#                                      article = new_art, date_creation= commentaire.date_creation)
#         article.delete()
#
#     return render(request, 'blog/accueil.html')
