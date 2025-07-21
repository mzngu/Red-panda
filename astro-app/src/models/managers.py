from django.contrib.auth.models import BaseUserManager
from django.utils import timezone

class UtilisateurManager(BaseUserManager):
    """
    Manager pour le modèle Utilisateur personnalisé.
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Crée et sauvegarde un utilisateur avec l'email et le mot de passe donnés.
        """
        if not email:
            raise ValueError("L'adresse email est obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Crée et sauvegarde un superutilisateur.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        # On définit des valeurs par défaut pour les champs obligatoires qui ne sont pas
        # demandés par la commande `createsuperuser`.
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('date_naissance', timezone.now().date())

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)