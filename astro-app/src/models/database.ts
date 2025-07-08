// Ce fichier simule les données de votre base de données.

export interface Utilisateur {
  id: number;
  nom: string;
  prenom: string;
  date_naissance: string;
  email: string;
  role: 'admin' | 'utilisateur';
}

export interface Ordonnance {
  id: number;
  utilisateur_id: number;
  nom: string;
  date: string;
  nom_docteur: string;
  type_docteur: string;
}

export interface Medicament {
  id: number;
  ordonnance_id: number;
  nom: string;
  dose: string;
}

// Données d'exemple
export const utilisateurs: Utilisateur[] = [
  { id: 1, nom: "Dupont", prenom: "Jean", date_naissance: "1985-05-15", email: "jean.dupont@example.com", role: "utilisateur" }
];

export const ordonnances: Ordonnance[] = [
  { id: 101, utilisateur_id: 1, nom: "Ordonnance Rhume", date: "2023-10-26", nom_docteur: "Dr. Martin", type_docteur: "Généraliste" },
  { id: 102, utilisateur_id: 1, nom: "Ordonnance Allergie", date: "2023-04-10", nom_docteur: "Dr. Lefebvre", type_docteur: "Allergologue" }
];

export const medicaments: Medicament[] = [
  { id: 1001, ordonnance_id: 101, nom: "Paracétamol", dose: "1g, 3 fois/jour" },
  { id: 1002, ordonnance_id: 101, nom: "Sirop Toux", dose: "1 cuillère, 3 fois/jour" },
  { id: 1003, ordonnance_id: 102, nom: "Antihistaminique", dose: "1 comprimé/jour" }
];