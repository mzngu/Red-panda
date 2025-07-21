from django.apps import AppConfig

class ModelsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'models'

    def ready(self):
        """
        Importe les modèles ici pour éviter les erreurs d'importation circulaire
        lors de l'initialisation de Django, notamment avec un modèle Utilisateur personnalisé.
        """
        # On importe uniquement les modèles pour les enregistrer auprès de Django.
        # C'est la manière la plus sûre de le faire.
        from . import utilisateur, ordonnance, medicament, allergie, antecedent