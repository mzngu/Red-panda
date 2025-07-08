from django.db import models
from .ordonnance import Ordonnance

class Medicament(models.Model):
    ordonnance = models.ForeignKey(Ordonnance, related_name='medicaments', on_delete=models.CASCADE)
    nom = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    dose = models.CharField(max_length=255, null=True, blank=True)
    composant = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.nom