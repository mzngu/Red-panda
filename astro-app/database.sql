CREATE TABLE IF NOT EXISTS utilisateur (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT,
    prenom TEXT,
    date_naissance DATE,
    email TEXT NOT NULL UNIQUE,
    mot_de_passe TEXT NOT NULL,
    numero_telephone TEXT,
    role TEXT NOT NULL CHECK (role IN ('admin', 'utilisateur'))
);

CREATE TABLE IF NOT EXISTS ordonnance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilisateur_id INTEGER NOT NULL,
    nom TEXT,
    date_ordonnance DATE NOT NULL,
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS medicaments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ordonnance_id INTEGER NOT NULL,
    nom TEXT,
    description_medicaments TEXT,
    dose TEXT,
    composant TEXT,
    FOREIGN KEY (ordonnance_id) REFERENCES ordonnance(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS allergies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilisateur_id INTEGER NOT NULL,
    nom TEXT,
    description_allergie TEXT,
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS antecedent_medical (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilisateur_id INTEGER NOT NULL,
    description TEXT,
    nom TEXT,
    date_diagnostic DATE,
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id) ON DELETE CASCADE
);
