from django.contrib.auth.models import BaseUserManager

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
        return self.create_user(email, password, **extra_fields)