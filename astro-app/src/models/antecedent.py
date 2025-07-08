from django.db import models
from .utilisateur import Utilisateur

class AntecedentMedical(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, related_name='antecedents_medicaux', on_delete=models.CASCADE)
    type = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    nom = models.CharField(max_length=255)
    raison = models.TextField(null=True, blank=True)
    date_diagnostic = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.nom