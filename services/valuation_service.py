import os
import sys
import math

# Ajouter le chemin parent pour pouvoir importer db_manager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import get_db_connection

class ValuationService:
    def __init__(self):
        self.weights = None  # [intercept, w_surface, w_rooms, w_bedrooms, w_age, w_city_m2, w_type_m2]
        self.mean_values = None
        self.std_values = None
        self.r2_score = 0.0
        self.mae = 0.0
        self.is_trained = False
        
    def train_model(self):
        # Entraine un modele de regression lineaire multi-variables en Python pur
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Recuperer les donnees de tous les biens (vendus et disponibles)
        cursor.execute("""
            SELECT p.price, p.surface, p.rooms, p.bedrooms, (2026 - p.year_built) as age, 
                   p.city, p.type
            FROM properties p
        """)
        rows = cursor.fetchall()
        conn.close()
        
        if len(rows) < 10:
            print("Pas assez de donnees pour entrainer le modele.")
            return False
            
        # Calcul des moyennes des prix au m2 par ville et par type pour servir de variables explicatives
        city_prices = {}
        type_prices = {}
        for r in rows:
            c, t, p, s = r['city'], r['type'], r['price'], r['surface']
            if s > 0:
                city_prices.setdefault(c, []).append(p / s)
                type_prices.setdefault(t, []).append(p / s)
                
        self.city_avg_m2 = {c: sum(lst)/len(lst) for c, lst in city_prices.items()}
        self.type_avg_m2 = {t: sum(lst)/len(lst) for t, lst in type_prices.items()}
        
        # Preparation de la matrice X et du vecteur Y
        # Features: [intercept, surface, rooms, bedrooms, age, city_avg_m2, type_avg_m2]
        X = []
        Y = []
        for r in rows:
            c_m2 = self.city_avg_m2.get(r['city'], 4000)
            t_m2 = self.type_avg_m2.get(r['type'], 4000)
            X.append([
                1.0, # Intercept
                float(r['surface']),
                float(r['rooms']),
                float(r['bedrooms']),
                float(r['age']),
                float(c_m2),
                float(t_m2)
            ])
            Y.append(float(r['price']))
            
        # Normalisation des variables (StandardScaler fait maison pour stabiliser la descente de gradient)
        n_samples = len(X)
        n_features = len(X[0])
        
        # Moyennes et ecart-types des features (sauf l'intercept a l'index 0)
        self.mean_values = [0.0] * n_features
        self.std_values = [1.0] * n_features
        
        for j in range(1, n_features):
            col = [X[i][j] for i in range(n_samples)]
            self.mean_values[j] = sum(col) / n_samples
            # Variance
            variance = sum((x - self.mean_values[j])**2 for x in col) / n_samples
            self.std_values[j] = math.sqrt(variance) if variance > 0 else 1.0
            
        # Normaliser X
        X_norm = []
        for i in range(n_samples):
            row_norm = [1.0]
            for j in range(1, n_features):
                val = (X[i][j] - self.mean_values[j]) / self.std_values[j]
                row_norm.append(val)
            X_norm.append(row_norm)
            
        # Descente de gradient pour ajuster les poids
        self.weights = [0.0] * n_features
        # Ajuster le point de depart de l'intercept a la moyenne de Y pour converger plus vite
        self.weights[0] = sum(Y) / n_samples
        
        learning_rate = 0.05
        epochs = 1500
        
        for epoch in range(epochs):
            gradients = [0.0] * n_features
            for i in range(n_samples):
                # Prediction
                prediction = sum(self.weights[j] * X_norm[i][j] for j in range(n_features))
                error = prediction - Y[i]
                # Calcul des gradients
                for j in range(n_features):
                    gradients[j] += error * X_norm[i][j]
            
            # Mise a jour des poids
            for j in range(n_features):
                self.weights[j] -= (learning_rate * gradients[j]) / n_samples
                
        # Calcul de la precision : R2 et MAE
        y_mean = sum(Y) / n_samples
        ss_tot = sum((y - y_mean)**2 for y in Y)
        ss_res = 0.0
        abs_errors = []
        
        for i in range(n_samples):
            pred = sum(self.weights[j] * X_norm[i][j] for j in range(n_features))
            ss_res += (Y[i] - pred)**2
            abs_errors.append(abs(Y[i] - pred))
            
        self.r2_score = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
        self.mae = sum(abs_errors) / n_samples
        self.is_trained = True
        
        print(f"Modele entraine avec succes sur {n_samples} biens.")
        print(f"R2 Score : {self.r2_score:.4f}")
        print(f"Erreur Moyenne Absolue (MAE) : {self.mae:.2f} EUR")
        return True

    def estimate_price(self, surface, rooms, bedrooms, age, city, prop_type):
        # Estime le prix d'un bien en appliquant les poids du modele entraine
        if not self.is_trained:
            # Essayer d'entrainer a la volee
            success = self.train_model()
            if not success:
                # Fallback sur une estimation heuristique simple
                city_m2 = 4000
                type_factor = 1.0
                return surface * city_m2 * type_factor
                
        # Recuperer les moyennes du marche pour ce secteur
        city_m2 = self.city_avg_m2.get(city, sum(self.city_avg_m2.values())/len(self.city_avg_m2))
        type_m2 = self.type_avg_m2.get(prop_type, sum(self.type_avg_m2.values())/len(self.type_avg_m2))
        
        # Features brutes
        features = [1.0, float(surface), float(rooms), float(bedrooms), float(age), float(city_m2), float(type_m2)]
        
        # Normaliser les features (sauf intercept)
        features_norm = [1.0]
        for j in range(1, len(features)):
            val = (features[j] - self.mean_values[j]) / self.std_values[j]
            features_norm.append(val)
            
        # Calcul du prix estime
        estimated_price = sum(self.weights[j] * features_norm[j] for j in range(len(features_norm)))
        
        # Borner le prix pour eviter des valeurs negatives absurdes sur de mauvaises entrees
        min_price = surface * city_m2 * 0.5
        return max(min_price, round(estimated_price, -2))
