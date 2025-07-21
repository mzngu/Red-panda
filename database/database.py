from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Import des modèles
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.base import Base

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT_STR = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

# Valider que toutes les variables d'environnement nécessaires sont définies
if not all([DB_USER, DB_PASSWORD, DB_NAME]):
    logger.critical("FATAL: Configuration de la base de données manquante. Veuillez définir les variables d'environnement DB_USER, DB_PASSWORD et DB_NAME.")
    raise ValueError("Configuration de la base de données manquante.")

# Analyser le port en toute sécurité
try:
    db_port = int(DB_PORT_STR)
except (ValueError, TypeError):
    logger.warning(f"Valeur DB_PORT invalide: '{DB_PORT_STR}'. Utilisation du port par défaut 5432.")
    db_port = 5432

def create_database_if_not_exists():
    """
    Crée la base de données si elle n'existe pas.
    """
    try:
        # Se connecter à PostgreSQL (base par défaut)
        conn = psycopg2.connect(
            host=DB_HOST,
            port=db_port,
            user=DB_USER,
            password=DB_PASSWORD,
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        cursor = conn.cursor()
        
        # Vérifier si la base existe
        cursor.execute(
            "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s",
            (DB_NAME,)
        )
        
        if not cursor.fetchone():
            logger.info(f"Création de la base de données '{DB_NAME}'...")
            cursor.execute(f'CREATE DATABASE "{DB_NAME}"')
            logger.info(f"Base de données '{DB_NAME}' créée avec succès!")
        else:
            logger.info(f"La base de données '{DB_NAME}' existe déjà.")
            
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        logger.error(f"Erreur lors de la création de la base de données: {e}")
        raise
    except Exception as e:
        logger.error(f"Erreur inattendue lors de la création de la base de données: {e}")
        raise

# Créer la base de données si elle n'existe pas
create_database_if_not_exists()

# Construire l'URL de la base de données
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{db_port}/{DB_NAME}"

# L'argument connect_args n'est plus nécessaire pour PostgreSQL.
engine = create_engine(
    DATABASE_URL, 
    echo=True # echo=True est utile pour le développement, pour voir les requêtes SQL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """
    Crée toutes les tables dans la base de données.
    A n'appeler qu'une seule fois au démarrage de l'application.
    """
    # Import tous les modèles pour s'assurer qu'ils sont enregistrés
    from models import utilisateur, ordonnance, medicament, allergie, antecedent
    
    logger.info("Initialisation de la base de données et création des tables si elles n'existent pas...")
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()