-- Schéma de Base de Données SQLite pour Ymmo

PRAGMA foreign_keys = ON;

-- 1. Table des Agences (Le siège à Aix-en-Provence + 12 agences nationales)
CREATE TABLE IF NOT EXISTS agencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    address TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    manager_name TEXT NOT NULL
);

-- 2. Table des Agents (Les commerciaux et gestionnaires)
CREATE TABLE IF NOT EXISTS agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('agent', 'manager', 'admin')),
    agency_id INTEGER NOT NULL,
    FOREIGN KEY (agency_id) REFERENCES agencies(id) ON DELETE CASCADE
);

-- 3. Table des Biens Immobiliers
CREATE TABLE IF NOT EXISTS properties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('maison', 'appartement', 'bureau', 'commercial')),
    status TEXT NOT NULL CHECK(status IN ('available', 'sold')) DEFAULT 'available',
    price REAL NOT NULL,
    surface REAL NOT NULL,
    rooms INTEGER NOT NULL,
    bedrooms INTEGER NOT NULL,
    city TEXT NOT NULL,
    address TEXT NOT NULL,
    zip_code TEXT NOT NULL,
    latitude REAL,
    longitude REAL,
    year_built INTEGER,
    image_url TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    agency_id INTEGER NOT NULL,
    agent_id INTEGER NOT NULL,
    FOREIGN KEY (agency_id) REFERENCES agencies(id) ON DELETE CASCADE,
    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE
);

-- 4. Table de l'Historique des Transactions (pour l'analyse de données)
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER,
    client_name TEXT NOT NULL,
    client_email TEXT NOT NULL,
    client_phone TEXT NOT NULL,
    agent_id INTEGER NOT NULL,
    price REAL NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('buy', 'sell')) DEFAULT 'buy',
    date DATE NOT NULL,
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE SET NULL,
    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE
);

-- 5. Table des Leads / Demandes clients
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    message TEXT NOT NULL,
    property_id INTEGER,
    status TEXT NOT NULL CHECK(status IN ('pending', 'contacted', 'completed')) DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE SET NULL
);

-- Index pour optimiser les requêtes fréquentes
CREATE INDEX IF NOT EXISTS idx_properties_city ON properties(city);
CREATE INDEX IF NOT EXISTS idx_properties_price ON properties(price);
CREATE INDEX IF NOT EXISTS idx_properties_status ON properties(status);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
