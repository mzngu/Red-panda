from django.contrib import admin
from django.urls import path, include
<<<<<<< HEAD
from rest_framework.authtoken import views as authtoken_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # Route pour obtenir un token d'authentification
    path('api/token-auth/', authtoken_views.obtain_auth_token, name='api_token_auth'),
=======

urlpatterns = [
    path('admin/', admin.site.urls),
>>>>>>> 20436fa (modification BDD + mise à jour code)
    # On connecte toutes les URLs de notre API sous le préfixe /api/
    path('api/', include('models.urls')),
]