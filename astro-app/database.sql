CREATE TABLE IF NOT EXISTS utilisateur (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    date_naissance DATE NOT NULL,
    nationalite TEXT,
    adresse TEXT,
    code_postal TEXT,
    email TEXT NOT NULL UNIQUE,
    mot_de_passe TEXT NOT NULL,
    numero_telephone TEXT,
    role TEXT NOT NULL CHECK (role IN ('admin', 'utilisateur'))
);

CREATE TABLE IF NOT EXISTS ordonnance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilisateur_id INTEGER NOT NULL,
    nom TEXT NOT NULL,
    lieu TEXT,
    date DATE NOT NULL,
    details TEXT,
    nom_docteur TEXT NOT NULL,
    type_docteur TEXT NOT NULL,
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS medicaments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ordonnance_id INTEGER NOT NULL,
    nom TEXT NOT NULL,
    description TEXT,
    dose TEXT,
    composant TEXT,
    FOREIGN KEY (ordonnance_id) REFERENCES ordonnance(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS allergies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilisateur_id INTEGER NOT NULL,
    nom TEXT NOT NULL,
    description TEXT,
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS antecedent_medical (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilisateur_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    description TEXT,
    nom TEXT NOT NULL,
    raison TEXT,
    date_diagnostic DATE,
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id) ON DELETE CASCADE
);
