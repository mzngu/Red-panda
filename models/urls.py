from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UtilisateurViewSet,
    OrdonnanceViewSet,
    MedicamentViewSet,
    AllergieViewSet,
    AntecedentMedicalViewSet,
    ChatbotView,
)

router = DefaultRouter()
router.register(r'utilisateurs', UtilisateurViewSet, basename='utilisateur')
router.register(r'ordonnances', OrdonnanceViewSet, basename='ordonnance')
router.register(r'medicaments', MedicamentViewSet, basename='medicament')
router.register(r'allergies', AllergieViewSet, basename='allergie')
router.register(r'antecedents', AntecedentMedicalViewSet, basename='antecedentmedical')

urlpatterns = [
    path('', include(router.urls)),
    path('chat/', ChatbotView.as_view(), name='chatbot'),
]