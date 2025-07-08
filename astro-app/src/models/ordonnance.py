from django.db import models
from .utilisateur import Utilisateur

class Ordonnance(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, related_name='ordonnances', on_delete=models.CASCADE)
    nom = models.CharField(max_length=255)
    lieu = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateField()
    details = models.TextField(null=True, blank=True)
    nom_docteur = models.CharField(max_length=255)
    type_docteur = models.CharField(max_length=255)

    def __str__(self):
        return self.nom