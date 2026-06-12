import os
import sys
# Ajouter le chemin parent pour pouvoir importer db_manager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import get_db_connection

class AnalyticsService:
    def get_general_stats(self):
        """Récupère les KPI généraux pour le tableau de bord."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Volume d'affaires cumulé (Chiffre d'Affaires total)
        cursor.execute("SELECT SUM(price) FROM transactions WHERE type='buy'")
        total_sales_volume = cursor.fetchone()[0] or 0.0
        
        # Nombre de transactions
        cursor.execute("SELECT COUNT(*) FROM transactions")
        total_transactions = cursor.fetchone()[0] or 0
        
        # Nombre de biens actifs en catalogue
        cursor.execute("SELECT COUNT(*) FROM properties WHERE status='available'")
        active_properties = cursor.fetchone()[0] or 0
        
        # Nombre de clients en attente (leads pending)
        cursor.execute("SELECT COUNT(*) FROM leads WHERE status='pending'")
        pending_leads = cursor.fetchone()[0] or 0
        
        # Nombre total de collaborateurs
        cursor.execute("SELECT COUNT(*) FROM agents")
        total_agents = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "total_sales_volume": total_sales_volume,
            "total_transactions": total_transactions,
            "active_properties": active_properties,
            "pending_leads": pending_leads,
            "total_agents": total_agents
        }

    def get_sales_by_city(self):
        """Calcule la répartition des ventes et prix moyen par m² par ville (SQL Avancé)."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Requête avec jointures, agrégations et calculs de ratios
        cursor.execute("""
            SELECT 
                p.city, 
                COUNT(t.id) as sales_count,
                SUM(t.price) as total_revenue,
                ROUND(AVG(t.price), 0) as avg_price,
                ROUND(AVG(p.price / p.surface), 0) as avg_price_m2
            FROM transactions t
            JOIN properties p ON t.property_id = p.id
            GROUP BY p.city
            ORDER BY total_revenue DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(r) for r in rows]

    def get_sales_by_type(self):
        """Calcule la répartition des ventes par type de bien immobilier."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                p.type,
                COUNT(t.id) as sales_count,
                SUM(t.price) as total_revenue,
                ROUND(AVG(t.price), 0) as avg_price
            FROM transactions t
            JOIN properties p ON t.property_id = p.id
            GROUP BY p.type
            ORDER BY sales_count DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(r) for r in rows]

    def get_sales_trends(self):
        """Récupère l'historique mensuel des ventes pour dessiner la courbe de tendance."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Requête pour extraire l'année et le mois et regrouper
        cursor.execute("""
            SELECT 
                DATE_FORMAT(date, '%Y-%m') as month_label,
                COUNT(id) as sales_count,
                SUM(price) as monthly_revenue
            FROM transactions
            GROUP BY month_label
            ORDER BY month_label ASC
        """)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(r) for r in rows]

    def get_top_agencies(self):
        """Classe le top 5 des agences par chiffre d'affaires cumulé."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                a.name as agency_name,
                a.city,
                COUNT(t.id) as sales_count,
                SUM(t.price) as total_revenue
            FROM transactions t
            JOIN agents ag ON t.agent_id = ag.id
            JOIN agencies a ON ag.agency_id = a.id
            GROUP BY a.id
            ORDER BY total_revenue DESC
            LIMIT 5
        """)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(r) for r in rows]

    def get_top_agents(self):
        """Classe le top 5 des meilleurs commerciaux nationaux Ymmo."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                ag.name as agent_name,
                a.name as agency_name,
                COUNT(t.id) as sales_count,
                SUM(t.price) as total_revenue
            FROM transactions t
            JOIN agents ag ON t.agent_id = ag.id
            JOIN agencies a ON ag.agency_id = a.id
            GROUP BY ag.id
            ORDER BY total_revenue DESC
            LIMIT 5
        """)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(r) for r in rows]

    def get_hot_zones_recommendations(self):
        """Analyse statistique pour identifier et recommander les zones d'achat à fort potentiel."""
        # Nous analysons :
        # 1. Les zones à plus forte liquidité (nombre de ventes le plus élevé)
        # 2. Les zones les plus abordables (prix au m² le plus bas pour les acheteurs)
        # 3. Les zones premium (les plus recherchées, prix au m² le plus élevé)
        sales_by_city = self.get_sales_by_city()
        
        if not sales_by_city:
            return []
            
        # Trier par volume de transactions (Liquidité)
        sorted_by_volume = sorted(sales_by_city, key=lambda x: x['sales_count'], reverse=True)
        # Trier par prix au m² (Abordabilité)
        sorted_by_price_m2 = sorted(sales_by_city, key=lambda x: x['avg_price_m2'])
        
        recommendations = []
        
        # 1. Zone dynamique (Liquidité maximale)
        top_liq = sorted_by_volume[0]
        recommendations.append({
            "city": top_liq['city'],
            "type": "Zone Premium Dynamique",
            "title": f"Marché ultra-liquide à {top_liq['city']}",
            "description": f"Avec {top_liq['sales_count']} ventes enregistrées, {top_liq['city']} est la ville la plus active du réseau Ymmo. "
                           f"Idéal pour revendre rapidement ou sécuriser un investissement locatif avec un faible taux de vacance.",
            "metric": f"{top_liq['avg_price_m2']} €/m² moyen"
        })
        
        # 2. Zone opportunité / bon marché
        top_opp = sorted_by_price_m2[0]
        recommendations.append({
            "city": top_opp['city'],
            "type": "Opportunité Premier Achat",
            "title": f"Secteur accessible à {top_opp['city']}",
            "description": f"{top_opp['city']} présente le prix d'entrée le plus compétitif du marché à seulement {top_opp['avg_price_m2']} €/m². "
                           f"Parfait pour les primo-accédants cherchant à maximiser leur surface habitable ou les investisseurs à haut rendement brut.",
            "metric": f"{top_opp['avg_price_m2']} €/m² moyen"
        })
        
        # 3. Zone haut de gamme
        top_premium = sorted_by_price_m2[-1]
        recommendations.append({
            "city": top_premium['city'],
            "type": "Investissement Patrimonial",
            "title": f"Placement de prestige à {top_premium['city']}",
            "description": f"Le prix moyen culmine à {top_premium['avg_price_m2']} €/m² à {top_premium['city']}. "
                           f"Un marché patrimonial d'exception garantissant une excellente conservation de la valeur et ciblant une clientèle locative à haut revenu.",
            "metric": f"{top_premium['avg_price_m2']} €/m² moyen"
        })
        
        return recommendations
