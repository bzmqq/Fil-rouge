import sqlite3
import random
import os
import sys
from datetime import datetime, timedelta

# Ajouter le chemin parent pour pouvoir importer db_manager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import get_db_connection, init_db, DB_PATH

# Villes et tarifs de base au m² (médianes réalistes en France)
CITIES_STATS = {
    "Aix-en-Provence": {"price_m2": 5300, "zip": "13100"},
    "Paris": {"price_m2": 10200, "zip": "75001"},
    "Marseille": {"price_m2": 3700, "zip": "13001"},
    "Lyon": {"price_m2": 4900, "zip": "69001"},
    "Toulouse": {"price_m2": 3600, "zip": "31000"},
    "Nice": {"price_m2": 4800, "zip": "06000"},
    "Nantes": {"price_m2": 3800, "zip": "44000"},
    "Strasbourg": {"price_m2": 3500, "zip": "67000"},
    "Montpellier": {"price_m2": 3400, "zip": "34000"},
    "Bordeaux": {"price_m2": 4500, "zip": "33000"},
    "Lille": {"price_m2": 3300, "zip": "59000"},
    "Rennes": {"price_m2": 3900, "zip": "35000"},
    "Reims": {"price_m2": 2700, "zip": "51100"}
}

# Noms et prénoms pour génération aléatoire
FIRST_NAMES = ["Jean", "Pierre", "Marie", "Sophie", "Thomas", "Nicolas", "Julien", "Lucas", "Camille", "Léa", "Chloé", "Antoine", "Sarah", "Julie", "Alexandre", "David", "Laurent", "Isabelle", "Sandrine", "Franck"]
LAST_NAMES = ["Martin", "Bernard", "Thomas", "Petit", "Robert", "Richard", "Durand", "Dubois", "Moreau", "Laurent", "Simon", "Michel", "Lefebvre", "Leroy", "Roux", "David", "Bertrand", "Morel", "Fournier", "Girard"]

STREETS = ["Rue de la République", "Avenue des Belges", "Boulevard Mirabeau", "Rue Paradis", "Avenue de la Grande Armée", "Rue de la Paix", "Avenue Jean Jaurès", "Boulevard Haussmann", "Rue des Fleurs", "Chemin des Romains", "Avenue de l'Europe", "Rue de la Gare"]

PROPERTY_TITLES = {
    "maison": [
        "Magnifique villa contemporaine avec piscine",
        "Maison de ville pleine de charme avec jardinet",
        "Grande maison familiale avec grand jardin arboré",
        "Maison de caractère en pierre avec vue dégagée",
        "Villa d'architecte lumineuse aux prestations haut de gamme"
    ],
    "appartement": [
        "Superbe appartement bourgeois haussmannien",
        "Studio moderne et optimisé idéal investisseur",
        "Bel appartement T3 traversant avec grand balcon",
        "Duplex d'exception avec terrasse panoramique",
        "Appartement T2 lumineux proche commerces et transports"
    ],
    "bureau": [
        "Plateau de bureaux modernes et câblés en plein centre",
        "Bureaux spacieux et lumineux dans quartier d'affaires",
        "Local professionnel idéal cabinet médical ou conseil",
        "Espace de coworking ou bureaux d'entreprise divisibles"
    ],
    "commercial": [
        "Boutique d'angle avec belle vitrine sur axe passant",
        "Grand local commercial avec réserve et accès livraisons",
        "Fonds de commerce restaurant avec terrasse",
        "Emplacement commercial n°1 en zone piétonne"
    ]
}

def generate_price(city, prop_type, surface, rooms, age_years=10, is_transaction=False):
    """Génère un prix cohérent basé sur des règles de marché réelles + bruit aléatoire."""
    base_m2 = CITIES_STATS[city]["price_m2"]
    
    # Ajustement selon le type de bien
    type_factors = {
        "maison": 1.10,       # Les maisons coûtent un peu plus cher au m² (jardin, calme)
        "appartement": 1.00,   # Référence
        "bureau": 1.15,      # Bureaux (secteur tertiaire)
        "commercial": 1.25   # Locaux commerciaux (premium emplacement)
    }
    factor = type_factors[prop_type]
    
    # Ajustement selon le nombre de pièces
    # Plus il y a de pièces pour une même surface, plus la valeur d'usage est élevée,
    # mais une surface trop cloisonnée peut aussi perdre de la valeur. Règle simplifiée :
    rooms_ratio = (rooms / (surface / 25)) if surface > 0 else 1
    rooms_factor = 0.95 if rooms_ratio < 0.6 else (1.05 if rooms_ratio < 1.2 else 0.90)
    
    # Ajustement selon l'ancienneté (les biens neufs/récents valent plus)
    age_factor = 1.15 if age_years < 5 else (1.00 if age_years < 20 else 0.85)
    
    # Calcul du prix théorique
    theoretical_price = surface * base_m2 * factor * rooms_factor * age_factor
    
    # Ajout d'un bruit aléatoire (±15% pour simuler les négociations et la qualité intrinsèque du bien)
    noise = random.uniform(0.85, 1.15)
    final_price = theoretical_price * noise
    
    # Les transactions historiques sont souvent un peu moins chères si on remonte dans le temps
    if is_transaction:
        # e.g., baisse de ~3% par an en remontant vers 2022
        pass
        
    return round(final_price, -2) # Arrondi à la centaine d'euros près

def seed_database():
    # Supprimer la base de données existante pour repartir de zéro
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print("Ancienne base de données supprimée pour un seeding propre.")
        except Exception as e:
            print(f"Note: Impossible de supprimer l'ancienne base : {e}")
            
    # S'assurer que le fichier DB et le schéma sont initialisés
    init_db()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("Début du seeding...")
    
    # 1. Insertion des Agences (Siège + 12 agences)
    print("Génération des agences...")
    agencies_data = []
    
    # Siège social
    agencies_data.append((
        "Ymmo Siège Social",
        "Aix-en-Provence",
        "15 Avenue des Belges",
        "04 42 10 20 30",
        "siege@ymmo.fr",
        "Pierre Martin"
    ))
    
    # 12 Agences nationales
    for city in list(CITIES_STATS.keys()):
        if city == "Aix-en-Provence":
            continue # Le siège y est déjà
        
        name = f"Ymmo {city}"
        address = f"{random.randint(1, 150)} {random.choice(STREETS)}"
        phone = f"0{random.choice([1, 2, 3, 4, 5])} {random.randint(40, 99)} {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)}"
        email = f"agence.{city.lower().replace('-', '')}@ymmo.fr"
        manager = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        
        agencies_data.append((name, city, address, phone, email, manager))
        
    cursor.executemany("""
        INSERT INTO agencies (name, city, address, phone, email, manager_name)
        VALUES (?, ?, ?, ?, ?, ?)
    """, agencies_data)
    conn.commit()
    
    # Récupérer les ID des agences
    cursor.execute("SELECT id, name, city FROM agencies")
    agencies = cursor.fetchall()
    agency_ids = {a['city']: a['id'] for a in agencies}
    
    # 2. Insertion des Agents (5 par agence = 65 agents au total)
    print("Génération des agents/commerciaux...")
    agents_data = []
    agent_id_counter = 1
    agency_agents = {} # agency_id -> list of agent_ids
    
    for agency in agencies:
        a_id = agency['id']
        agency_agents[a_id] = []
        
        # 1 Manager
        m_first = random.choice(FIRST_NAMES)
        m_last = random.choice(LAST_NAMES)
        m_name = f"{m_first} {m_last}"
        m_email = f"{m_first.lower()}.{m_last.lower()}.{agency['city'].lower().replace('-', '')}@ymmo.fr"
        m_phone = f"06 {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)}"
        agents_data.append((m_name, m_email, m_phone, 'manager', a_id))
        agency_agents[a_id].append(agent_id_counter)
        agent_id_counter += 1
        
        # 4 Agents commerciaux
        for idx in range(1, 5):
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            name = f"{first} {last}"
            email = f"{first.lower()}.{last.lower()}.{idx}.{agency['city'].lower().replace('-', '')}@ymmo.fr"
            phone = f"06 {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)}"
            agents_data.append((name, email, phone, 'agent', a_id))
            agency_agents[a_id].append(agent_id_counter)
            agent_id_counter += 1
            
    # Ajouter un admin général au siège
    admin_first, admin_last = "Alexandre", "Admin"
    agents_data.append((
        f"{admin_first} {admin_last}", 
        "admin@ymmo.fr", 
        "06 00 00 00 00", 
        "admin", 
        agency_ids["Aix-en-Provence"]
    ))
    
    cursor.executemany("""
        INSERT INTO agents (name, email, phone, role, agency_id)
        VALUES (?, ?, ?, ?, ?)
    """, agents_data)
    conn.commit()
    
    # 3. Insertion des Transactions Historiques (1000+ ventes de 2022 à 2026)
    print("Génération de l'historique des ventes (1000+ transactions)...")
    transactions_data = []
    
    # Date de début (janvier 2022) et fin (mai 2026)
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2026, 5, 1)
    days_between = (end_date - start_date).days
    
    # Pour avoir des graphiques d'analyse de données superbes, nous allons simuler
    # un volume croissant de ventes au fil des ans, avec une saisonnalité (plus de ventes au printemps/été)
    num_transactions = 1100
    
    for i in range(num_transactions):
        # Ville aléatoire
        city = random.choice(list(CITIES_STATS.keys()))
        a_id = agency_ids[city]
        ag_id = random.choice(agency_agents[a_id]) # Commercial de cette agence
        
        # Caractéristiques aléatoires cohérentes
        prop_type = random.choice(['maison', 'appartement', 'bureau', 'commercial'])
        
        if prop_type == 'maison':
            surface = round(random.uniform(70, 250), 1)
            rooms = random.randint(3, 8)
            bedrooms = max(1, rooms - random.randint(2, 3))
        elif prop_type == 'appartement':
            surface = round(random.uniform(20, 120), 1)
            rooms = random.randint(1, 5)
            bedrooms = max(0, rooms - 1)
        elif prop_type == 'bureau':
            surface = round(random.uniform(40, 400), 1)
            rooms = random.randint(2, 12)
            bedrooms = 0
        else: # commercial
            surface = round(random.uniform(30, 300), 1)
            rooms = random.randint(1, 4)
            bedrooms = 0
            
        age_years = random.randint(0, 80)
        year_built = 2026 - age_years
        
        # Calcul du prix
        price = generate_price(city, prop_type, surface, rooms, age_years, is_transaction=True)
        
        # Inflation/tendance du marché : les prix en 2022 étaient légèrement inférieurs de 8% par rapport à 2026
        # Date aléatoire avec distribution
        rand_days = random.randint(0, days_between)
        trans_date = start_date + timedelta(days=rand_days)
        
        # Ajustement inflation
        years_diff = (trans_date - end_date).days / 365.25
        inflation_multiplier = 1 + (years_diff * 0.03) # 3% d'évolution annuelle
        price = round(price * inflation_multiplier, -2)
        
        client_name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        client_email = f"{client_name.lower().replace(' ', '.')}@example.com"
        client_phone = f"06 {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)}"
        
        address = f"{random.randint(1, 180)} {random.choice(STREETS)}"
        zip_code = CITIES_STATS[city]["zip"]
        title = f"{prop_type.capitalize()} vendu à {city}"
        description = f"Bien de type {prop_type} vendu avec succès par notre agence de {city}."
        image_url = "" # Pas d'image pour les biens d'archive
        
        cursor.execute("""
            INSERT INTO properties (
                title, description, type, status, price, surface, rooms, bedrooms,
                city, address, zip_code, latitude, longitude, year_built, image_url, agency_id, agent_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            title, description, prop_type, 'sold', price, surface, rooms, bedrooms,
            city, address, zip_code, None, None, year_built, image_url, a_id, ag_id
        ))
        property_id = cursor.lastrowid
        
        transactions_data.append((
            property_id,
            client_name,
            client_email,
            client_phone,
            ag_id,
            price,
            'buy',
            trans_date.strftime('%Y-%m-%d')
        ))
        
    cursor.executemany("""
        INSERT INTO transactions (property_id, client_name, client_email, client_phone, agent_id, price, type, date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, transactions_data)
    conn.commit()
    
    # 4. Insertion des Biens Disponibles Actuellement (Catalogue Actif - ~60 biens)
    print("Génération des biens actifs actuellement disponibles au catalogue (~60 biens)...")
    properties_data = []
    
    # Images d'illustration réalistes (génériques pour l'immobilier, libres de droit / unspash)
    images_db = {
        "maison": [
            "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=800&q=80"
        ],
        "appartement": [
            "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1484154218962-a197022b5858?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=800&q=80"
        ],
        "bureau": [
            "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1497215728101-856f4ea42174?auto=format&fit=crop&w=800&q=80"
        ],
        "commercial": [
            "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=800&q=80"
        ]
    }
    
    # Générer 5 biens par ville en moyenne
    for city in list(CITIES_STATS.keys()):
        a_id = agency_ids[city]
        
        for _ in range(5):
            prop_type = random.choices(
                ['maison', 'appartement', 'bureau', 'commercial'],
                weights=[40, 45, 10, 5],
                k=1
            )[0]
            
            # Caractéristiques
            if prop_type == 'maison':
                surface = round(random.uniform(80, 220), 1)
                rooms = random.randint(4, 7)
                bedrooms = max(1, rooms - random.randint(2, 3))
            elif prop_type == 'appartement':
                surface = round(random.uniform(30, 100), 1)
                rooms = random.randint(2, 4)
                bedrooms = max(1, rooms - 1)
            elif prop_type == 'bureau':
                surface = round(random.uniform(50, 200), 1)
                rooms = random.randint(2, 6)
                bedrooms = 0
            else: # commercial
                surface = round(random.uniform(40, 150), 1)
                rooms = random.randint(1, 3)
                bedrooms = 0
                
            age_years = random.randint(1, 50)
            year_built = 2026 - age_years
            
            price = generate_price(city, prop_type, surface, rooms, age_years, is_transaction=False)
            
            title = random.choice(PROPERTY_TITLES[prop_type])
            description = (
                f"Situé idéalement à {city}, ce bien de type {prop_type} saura vous séduire par ses prestations. "
                f"D'une surface habitable de {surface} m² comprenant {rooms} pièce(s), il offre un cadre de vie "
                f"privilégié, proche de toutes commodités. À visiter rapidement avec l'agence Ymmo de {city}."
            )
            
            address = f"{random.randint(1, 180)} {random.choice(STREETS)}"
            zip_code = CITIES_STATS[city]["zip"]
            
            # Coordonnées géographiques fictives autour de la ville (pour la crédibilité de la carte)
            latitude = 45.0 + random.uniform(-2.0, 2.0)
            longitude = 2.0 + random.uniform(-2.0, 2.0)
            
            image_url = random.choice(images_db[prop_type])
            
            agent_id = random.choice(agency_agents[a_id])
            
            properties_data.append((
                title, description, prop_type, 'available', price, surface, rooms, bedrooms,
                city, address, zip_code, latitude, longitude, year_built, image_url, a_id, agent_id
            ))
            
    cursor.executemany("""
        INSERT INTO properties (
            title, description, type, status, price, surface, rooms, bedrooms,
            city, address, zip_code, latitude, longitude, year_built, image_url, agency_id, agent_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, properties_data)
    conn.commit()
    
    # 5. Quelques leads / demandes clients pour peupler l'interface d'administration
    print("Génération de leads de contact d'exemple...")
    cursor.execute("SELECT id FROM properties LIMIT 10")
    recent_prop_ids = [p['id'] for p in cursor.fetchall()]
    
    leads_data = []
    messages = [
        "Bonjour, je suis très intéressé par ce bien. Est-il possible d'organiser une visite samedi prochain ?",
        "Je souhaiterais avoir plus d'informations concernant les charges de copropriété et la taxe foncière.",
        "Bonjour, ce bien correspond parfaitement à ma recherche. Je dispose d'un accord de principe de ma banque. Merci de me recontacter.",
        "Je voudrais savoir si le prix est négociable et s'il y a des travaux prévus dans l'immeuble."
    ]
    
    for p_id in recent_prop_ids:
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        name = f"{first} {last}"
        email = f"{first.lower()}.{last.lower()}@mail.com"
        phone = f"06 {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)}"
        msg = random.choice(messages)
        status = random.choice(['pending', 'contacted', 'completed'])
        
        leads_data.append((name, email, phone, msg, p_id, status))
        
    cursor.executemany("""
        INSERT INTO leads (name, email, phone, message, property_id, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, leads_data)
    conn.commit()
    
    # Affichage du bilan du seeding
    cursor.execute("SELECT COUNT(*) FROM agencies")
    c_agencies = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM agents")
    c_agents = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM properties")
    c_properties = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM transactions")
    c_transactions = cursor.fetchone()[0]
    
    print("\n--- Bilan du Seeding de la Base de Données ---")
    print(f"Agences créées     : {c_agencies} (Siège + 12 agences)")
    print(f"Agents créés       : {c_agents} (5 par agence + 1 admin)")
    print(f"Biens disponibles : {c_properties} actifs en catalogue")
    print(f"Transactions histor.: {c_transactions} ventes enregistrées de 2022 à 2026")
    print("---------------------------------------------\n")
    
    conn.close()
    print("Seeding complété avec succès !")

if __name__ == '__main__':
    seed_database()
