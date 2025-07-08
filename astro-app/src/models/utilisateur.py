from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UtilisateurManager

class Utilisateur(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('utilisateur', 'Utilisateur'),
    ]

    email = models.EmailField(unique=True)
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    date_naissance = models.DateField()
    nationalite = models.CharField(max_length=255, null=True, blank=True)
    adresse = models.TextField(null=True, blank=True)
    code_postal = models.CharField(max_length=20, null=True, blank=True)
    numero_telephone = models.CharField(max_length=20, null=True, blank=True)
    role = models.CharField(max_length=11, choices=ROLE_CHOICES)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UtilisateurManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom', 'prenom']

    def __str__(self):
        return f"{self.prenom} {self.nom}"