import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database.db')
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')

def get_db_connection():
    """Crée et retourne une connexion SQLite avec row_factory=dict pour faciliter l'accès."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Activer les clés étrangères pour garantir l'intégrité référentielle
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """Initialise la base de données en exécutant le script schema.sql si les tables n'existent pas."""
    print(f"Initialisation de la base de données à : {DB_PATH}")
    
    if not os.path.exists(SCHEMA_PATH):
        raise FileNotFoundError(f"Le fichier de schéma SQL est introuvable à : {SCHEMA_PATH}")
        
    conn = get_db_connection()
    try:
        with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        conn.executescript(schema_sql)
        conn.commit()
        print("Base de données initialisée avec succès avec le schéma SQL.")
    except Exception as e:
        conn.rollback()
        print(f"Erreur lors de l'initialisation de la base de données : {e}")
        raise e
    finally:
        conn.close()

if __name__ == '__main__':
    init_db()
