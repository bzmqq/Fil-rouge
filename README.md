# 🏡 Ymmo — Plateforme d'Estimation Immobilière IA & Tableau de Bord Business

Ymmo est une application web moderne de gestion et d'estimation immobilière. Elle combine un catalogue interactif de biens immobiliers, un moteur d'estimation de prix basé sur une **Intelligence Artificielle en Python pur** (sans dépendance à des bibliothèques de Machine Learning externes), et un **Tableau de Bord commercial (Dashboard)** analytique complet.

Ce projet est prêt à être poussé sur GitHub et est structuré de manière propre et professionnelle.

---

## ✨ Fonctionnalités Clés

1. **🏡 Catalogue Interactif & Recherche Multicritère** (`/search`) :
   * Recherche dynamique en temps réel par ville, type de bien, prix maximum, surface minimum et nombre de pièces.
   * Fiches de biens détaillées avec les coordonnées de l'agent immobilier responsable.

2. **🧠 Moteur d'Estimation IA (Machine Learning Maison)** (`/estimation`) :
   * Régression linéaire multivariée écrite de A à Z en Python pur (sans `scikit-learn`).
   * Normalisation des variables (*StandardScaler* fait maison) et entraînement par descente de gradient.
   * Prise en compte de multiples critères : surface, nombre de pièces, chambres, âge du bâtiment, prix moyen au m² de la ville, et prix moyen par type de bien.
   * Affichage transparent des performances du modèle pour l'utilisateur (Score $R^2$ et Erreur Moyenne Absolue / MAE).

3. **📊 Tableau de Bord Business & Management** (`/dashboard`) :
   * Analyse des performances des agences et des agents immobiliers.
   * Graphiques et visualisations des tendances de ventes, répartition par ville et par type de bien.
   * Recommandations intelligentes de "Zones chaudes" d'investissement.
   * Système de gestion des prospects (leads commerciaux) avec changement de statut à la volée.

4. **📖 Documentation Interactive (Livrable Académique)** (`/docs`) :
   * Page dédiée expliquant l'architecture technique, le modèle de données SQLite et les détails mathématiques du modèle de régression.

---

## 🛠️ Architecture du Projet

L'application suit une architecture modulaire et découplée :

```text
fil-rouge/
├── app.py                      # Point d'entrée principal (serveur Flask et API REST)
├── requirements.txt            # Dépendances du projet (uniquement Flask !)
├── database.db                 # Base de données SQLite (générée automatiquement)
├── database/
│   ├── db_manager.py           # Gestionnaire de connexion et initialisation de la DB
│   ├── schema.sql              # Schéma de création des tables SQLite
│   └── seed.py                 # Script de peuplement de données réalistes (biens, agents, leads...)
├── services/
│   ├── valuation_service.py    # Algorithme d'entraînement et d'estimation de l'IA (Régression linéaire)
│   └── analytics_service.py    # Calculs et statistiques pour le Dashboard
├── static/
│   ├── css/                    # Fichiers CSS (design premium, dark mode & glassmorphic)
│   └── js/                     # Scripts JS pour l'interactivité AJAX (recherche, estimation, dashboard)
└── templates/
    ├── index.html              # Page d'accueil vitrine
    ├── search.html             # Page de recherche
    ├── estimation.html         # Page d'estimation IA
    ├── dashboard.html          # Dashboard commercial
    └── docs.html               # Documentation interactive
```

---

## 🚀 Installation et Lancement

Suivez ces instructions pour installer et lancer le projet localement :

### 1. Cloner le dépôt
```bash
git clone <URL_DE_VOTRE_DEPOT_GITHUB>
cd fil-rouge
```

### 2. Créer et activer un environnement virtuel (optionnel mais recommandé)
Sur Windows :
```bash
python -m venv .venv
.venv\Scripts\activate
```
Sur macOS/Linux :
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Installer les dépendances
L'application Ymmo a été conçue pour être ultra-légère. Elle ne nécessite que Flask :
```bash
pip install -r requirements.txt
```

### 4. Lancer l'application
Démarrez le serveur de développement Flask :
```bash
python app.py
```

* **Initialisation automatique** : Si la base de données `database.db` n'existe pas, l'application exécute automatiquement les scripts SQL et génère des données de test réalistes via `seed.py`.
* **Entraînement de l'IA** : Le modèle prédictif s'entraîne automatiquement dès le démarrage de l'application à partir des données de la base.

### 5. Accéder à l'application
Ouvrez votre navigateur web et rendez-vous sur :
[http://localhost:5000](http://localhost:5000)

---

## 🤖 Focus Technique : Le Modèle d'Estimation IA

Le service d'estimation (`valuation_service.py`) utilise un algorithme de **descente de gradient par batch** pour optimiser les poids associés aux caractéristiques des biens. 

### Étapes de calcul :
1. **Extraction et enrichissement** : Récupération des données historiques et calcul des tarifs moyens au m² par ville et par type pour servir de variables explicatives contextuelles.
2. **Normalisation (Z-score)** : 
   $$x_{norm} = \frac{x - \mu}{\sigma}$$
   Cela garantit une convergence rapide et stable lors de la descente de gradient.
3. **Descente de gradient** : Ajustement itératif des poids pour minimiser l'erreur quadratique.
4. **Validation** : Calcul en temps réel du coefficient de détermination $R^2$ et de l'erreur absolue moyenne (MAE) pour évaluer la précision du modèle.

---

## 📝 Licence

Ce projet est sous licence MIT. N'hésitez pas à l'utiliser et à le modifier à votre guise !
