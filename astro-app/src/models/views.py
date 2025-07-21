from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .utilisateur import Utilisateur
from .ordonnance import Ordonnance
from .medicament import Medicament
from .allergie import Allergie
from .antecedent import AntecedentMedical
from .serializers import (
    UtilisateurSerializer,
    OrdonnanceSerializer,
    MedicamentSerializer,
    AllergieSerializer,
    AntecedentMedicalSerializer,
)
from services.service import generate_response as generate_ai_response
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
        """Sauvegarde le nouvel utilisateur. Le serializer doit gérer le hachage du mot de passe."""
        serializer.save()

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
        """
        Sauvegarde le nouveau médicament.
        Le client doit fournir l'ID de l'ordonnance dans le corps de la requête.
        """
        serializer.save()

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

class ChatbotView(APIView):
    """
    Vue pour interagir avec l'assistant médical Sorrel (Gemini AI).
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        prompt = request.data.get('prompt')
        if not prompt:
            return Response(
                {"error": "Un 'prompt' est requis dans le corps de la requête."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # On utilise un alias pour éviter un conflit de nom avec Response de DRF
            ai_response = generate_ai_response(prompt)
            return Response({"response": ai_response}, status=status.HTTP_200_OK)
        except Exception as e:
            # Idéalement, logguez l'erreur `e` pour le débogage
            return Response(
                {"error": "Une erreur est survenue lors de la communication avec l'assistant."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )