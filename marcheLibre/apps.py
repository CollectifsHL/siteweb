from django.apps import AppConfig

class MarcheLibreConfig(AppConfig):
    name = 'marcheLibre'

    def ready(self):
        from actstream import registry
        from django.contrib.auth.models import Group
        from blog.models import Article, Projet
        #from jardinpartage.models import Article as art_jardinpartage
        from ateliers.models import Atelier, InscriptionAtelier
        from fiches.models import Fiche, Atelier as fiche_at
        from vote.models import Votation
        registry.register(self.get_model('Profil'))
        registry.register(self.get_model('MessageGeneral'))
        registry.register(self.get_model('MessageGeneralCollectifsHL'))
        registry.register(self.get_model('Produit'))
        registry.register(self.get_model('Conversation'))
        registry.register(self.get_model('Produit'))
        registry.register(self.get_model('Produit_vegetal'))
        registry.register(self.get_model('Produit_service'))
        registry.register(self.get_model('Produit_objet'))
        registry.register(self.get_model('Produit_aliment'))
        registry.register(self.get_model('Suivis'))
        registry.register(self.get_model('Adhesion_collectifshl'))
        registry.register(Atelier)
        registry.register(InscriptionAtelier)
        registry.register(Fiche)
        registry.register(fiche_at)
        registry.register(Article)
        #registry.register(art_jardinpartage)
        registry.register(Projet)
        registry.register(Group)
        registry.register(Votation)