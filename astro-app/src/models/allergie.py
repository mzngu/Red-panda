from django.db import models
from .utilisateur import Utilisateur

class Allergie(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, related_name='allergies', on_delete=models.CASCADE)
    nom = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nom