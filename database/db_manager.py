import pymysql
import pymysql.cursors
import os

SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')

def load_env():
    """Charge les variables d'environnement à partir du fichier .env si présent."""
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    os.environ[key.strip()] = val.strip().strip('"').strip("'")

# Charger les variables d'environnement au démarrage
load_env()

class RowDict(dict):
    """Dictionnaire spécialisé qui permet l'accès par nom de colonne ou par index numérique."""
    def __init__(self, d):
        super().__init__(d)
        self._values = list(d.values())
        
    def __getitem__(self, key):
        if isinstance(key, int):
            try:
                return self._values[key]
            except IndexError:
                raise KeyError(key)
        return super().__getitem__(key)

class SafeDictCursor:
    """Wrapper de curseur MySQL assurant que fetchone/fetchall renvoient des RowDict."""
    def __init__(self, cursor):
        self._cursor = cursor
        
    def execute(self, *args, **kwargs):
        return self._cursor.execute(*args, **kwargs)
        
    def executemany(self, *args, **kwargs):
        return self._cursor.executemany(*args, **kwargs)
        
    def fetchone(self):
        row = self._cursor.fetchone()
        if row is None:
            return None
        return RowDict(row)
        
    def fetchall(self):
        rows = self._cursor.fetchall()
        return [RowDict(row) for row in rows]
        
    def close(self):
        return self._cursor.close()
        
    @property
    def lastrowid(self):
        return self._cursor.lastrowid
        
    def __iter__(self):
        for row in self._cursor:
            yield RowDict(row)
            
    def __getattr__(self, name):
        return getattr(self._cursor, name)

def get_db_connection():
    """Crée et retourne une connexion MySQL, configurée par variables d'environnement."""
    db_name = os.environ.get("DB_NAME", "ymmo_db")
    
    # Se connecter d'abord au serveur MySQL sans spécifier de base (pour parer à son absence)
    conn = pymysql.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", ""),
        port=int(os.environ.get("DB_PORT", 3306))
    )
    
    # Créer la base de données automatiquement si elle n'existe pas
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    cursor.close()
    
    # Sélectionner la base de données
    conn.select_db(db_name)
    
    # Surcharge la méthode cursor() pour retourner un curseur dictionnaire encapsulé par défaut.
    original_cursor = conn.cursor
    def dictionary_cursor(*args, **kwargs):
        kwargs.setdefault('cursor', pymysql.cursors.DictCursor)
        return SafeDictCursor(original_cursor(*args, **kwargs))
        
    conn.cursor = dictionary_cursor
    return conn

def init_db():
    """Initialise la base de données MySQL en exécutant le schéma DDL."""
    print("Initialisation de la base de données MySQL...")
    
    if not os.path.exists(SCHEMA_PATH):
        raise FileNotFoundError(f"Le fichier de schéma SQL est introuvable à : {SCHEMA_PATH}")
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
            
        # Diviser le script en requêtes individuelles séparées par des points-virgules
        statements = schema_sql.split(';')
        for statement in statements:
            statement = statement.strip()
            if statement:
                cursor.execute(statement)
            
        conn.commit()
        print("Base de données MySQL initialisée avec succès.")
    except Exception as e:
        conn.rollback()
        print(f"Erreur lors de l'initialisation de la base de données MySQL : {e}")
        raise e
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    init_db()
