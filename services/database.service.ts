import {
  utilisateurs,
  ordonnances,
  medicaments,
  type Utilisateur,
  type Ordonnance,
  type Medicament
} from '../astro-app/src/models/database.ts';

export interface ProfilComplet {
  utilisateur: Utilisateur;
  ordonnances: (Ordonnance & { medicaments: Medicament[] })[];
}

export class DatabaseService {
  async getProfilUtilisateur(utilisateurId: number): Promise<ProfilComplet | null> {
    const utilisateur = utilisateurs.find(u => u.id === utilisateurId);
    if (!utilisateur) return null;

    const ordonnancesUtilisateur = ordonnances.filter(
      (o) => o.utilisateur_id === utilisateur.id
    );

    const ordonnancesAvecMedicaments = ordonnancesUtilisateur.map(ordonnance => ({
      ...ordonnance,
      medicaments: medicaments.filter(m => m.ordonnance_id === ordonnance.id),
    }));

    return {
      utilisateur,
      ordonnances: ordonnancesAvecMedicaments,
    };
  }
}
