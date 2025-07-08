from rest_framework import viewsets
from rest_framework import permissions
from .models import Utilisateur, Ordonnance, Medicament, Allergie, AntecedentMedical
from .serializers import (
    UtilisateurSerializer,
    MedicamentSerializer,
    OrdonnanceSerializer,
    MedicamentSerializer,
    AllergieSerializer,
    AntecedentMedicalSerializer,
)
from .permissions import IsOwnerOrAdmin

class UtilisateurViewSet(viewsets.ModelViewSet):
    serializer_class = UtilisateurSerializer
    # Appliquer notre permission personnalisée
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        """
        Les administrateurs peuvent voir tous les utilisateurs.
        Les autres ne peuvent voir que leur propre profil.
        """
        user = self.request.user
        if user.is_staff:
            return Utilisateur.objects.all()
        return Utilisateur.objects.filter(pk=user.pk)
    def perform_create(self, serializer):
        """ne peut créer un utilisateur que via le manager"""
        return

class OrdonnanceViewSet(viewsets.ModelViewSet):
    serializer_class = OrdonnanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        """
        n'afficher que les ordonnances de l'utilisateur courant
        """
        return Ordonnance.objects.filter(utilisateur=self.request.user)
    def perform_create(self, serializer):
        """
        Assigne auto l'utilisateur courant à la nouvelle ordonnance
        """
        serializer.save(utilisateur=self.request.user)

class MedicamentViewSet(viewsets.ModelViewSet):
    serializer_class = MedicamentSerializer
    # Un médicament est lié à une ordonnance, la permission est donc héritée
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        """
        n'afficher que les medicaments de l'ordonnance de l'utilisateur courant
        """
        ordonnances = Ordonnance.objects.filter(utilisateur=self.request.user)
        return Medicament.objects.filter(ordonnance__in=ordonnances)
    def perform_create(self, serializer):
        return

class AllergieViewSet(viewsets.ModelViewSet):
    serializer_class = AllergieSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Cette vue ne doit retourner que les allergies de l'utilisateur actuel."""
        return Allergie.objects.filter(utilisateur=self.request.user)

    def perform_create(self, serializer):
        """Assigne automatiquement l'utilisateur actuel à la nouvelle allergie."""
        serializer.save(utilisateur=self.request.user)

class AntecedentMedicalViewSet(viewsets.ModelViewSet):
    serializer_class = AntecedentMedicalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Cette vue ne doit retourner que les antécédents de l'utilisateur actuel."""
        return AntecedentMedical.objects.filter(utilisateur=self.request.user)

    def perform_create(self, serializer):
        serializer.save(utilisateur=self.request.user)