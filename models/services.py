from django.db import transaction
from .ordonnance import Ordonnance
from .medicament import Medicament
from .utilisateur import Utilisateur
from typing import List, Dict, Any

@transaction.atomic
def create_ordonnance_with_medicaments(
    *,
    utilisateur: Utilisateur,
    nom: str,
    date: str,
    nom_docteur: str,
    type_docteur: str,
    medicaments_data: List[Dict[str, Any]]
) -> Ordonnance:
    """
    Crée une ordonnance et ses médicaments associés de manière atomique.
    C'est la fonction de service qui contient la logique métier.
    """
    ordonnance_data = {'nom': nom, 'date': date, 'nom_docteur': nom_docteur, 'type_docteur': type_docteur, 'utilisateur': utilisateur}
    ordonnance = Ordonnance.objects.create(**ordonnance_data)
    for medicament_data in medicaments_data:
        Medicament.objects.create(ordonnance=ordonnance, **medicament_data)
    return ordonnance