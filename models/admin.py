from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .utilisateur import Utilisateur
from .ordonnance import Ordonnance
from .medicament import Medicament
from .allergie import Allergie
from .antecedent import AntecedentMedical

class UtilisateurAdmin(UserAdmin):
    """
    Configuration personnalisée pour l'affichage du modèle Utilisateur dans l'admin.
    """
    list_display = ('email', 'nom', 'prenom', 'is_staff', 'is_active')
    search_fields = ('email', 'nom', 'prenom')
    ordering = ('email',)
    # Nécessaire car nous utilisons un modèle utilisateur personnalisé
    fieldsets = UserAdmin.fieldsets + (
        ('Informations Personnelles', {'fields': ('date_naissance', 'nationalite', 'adresse', 'code_postal', 'numero_telephone', 'role')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informations Personnelles', {'fields': ('nom', 'prenom', 'date_naissance', 'nationalite', 'adresse', 'code_postal', 'numero_telephone', 'role')}),
    )

admin.site.register(Utilisateur, UtilisateurAdmin)
admin.site.register(Ordonnance)
admin.site.register(Medicament)
admin.site.register(Allergie)
admin.site.register(AntecedentMedical)