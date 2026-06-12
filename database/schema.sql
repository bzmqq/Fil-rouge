-- Schéma de Base de Données MySQL pour Ymmo

-- Supprimer les tables existantes (pour réinitialisation lors du seed)
DROP TABLE IF EXISTS leads;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS properties;
DROP TABLE IF EXISTS agents;
DROP TABLE IF EXISTS agencies;

-- 1. Table des Agences (Le siège à Aix-en-Provence + 12 agences nationales)
CREATE TABLE IF NOT EXISTS agencies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    city VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    manager_name VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Table des Agents (Les commerciaux et gestionnaires)
CREATE TABLE IF NOT EXISTS agents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(50) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK(role IN ('agent', 'manager', 'admin')),
    agency_id INT NOT NULL,
    FOREIGN KEY (agency_id) REFERENCES agencies(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Table des Biens Immobiliers
CREATE TABLE IF NOT EXISTS properties (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description LONGTEXT NOT NULL,
    type VARCHAR(50) NOT NULL CHECK(type IN ('maison', 'appartement', 'bureau', 'commercial')),
    status VARCHAR(50) NOT NULL DEFAULT 'available' CHECK(status IN ('available', 'sold')),
    price DOUBLE NOT NULL,
    surface DOUBLE NOT NULL,
    rooms INT NOT NULL,
    bedrooms INT NOT NULL,
    city VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL,
    zip_code VARCHAR(20) NOT NULL,
    latitude DOUBLE,
    longitude DOUBLE,
    year_built INT,
    image_url VARCHAR(1024),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    agency_id INT NOT NULL,
    agent_id INT NOT NULL,
    FOREIGN KEY (agency_id) REFERENCES agencies(id) ON DELETE CASCADE,
    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE,
    INDEX idx_properties_city (city),
    INDEX idx_properties_price (price),
    INDEX idx_properties_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Table de l'Historique des Transactions (pour l'analyse de données)
CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    property_id INT,
    client_name VARCHAR(255) NOT NULL,
    client_email VARCHAR(255) NOT NULL,
    client_phone VARCHAR(50) NOT NULL,
    agent_id INT NOT NULL,
    price DOUBLE NOT NULL,
    type VARCHAR(50) NOT NULL DEFAULT 'buy' CHECK(type IN ('buy', 'sell')),
    date DATE NOT NULL,
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE SET NULL,
    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE,
    INDEX idx_transactions_date (date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Table des Leads / Demandes clients
CREATE TABLE IF NOT EXISTS leads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    message LONGTEXT NOT NULL,
    property_id INT,
    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'contacted', 'completed')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
