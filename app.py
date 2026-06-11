from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import os
import sys
import sqlite3

# Configurer les chemins
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database.db_manager import get_db_connection, init_db
from services.valuation_service import ValuationService
from services.analytics_service import AnalyticsService

app = Flask(__name__)
app.secret_key = 'ymmo_super_secret_dev_key'

# Initialiser la base de données au premier démarrage si nécessaire
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')
if not os.path.exists(DB_PATH):
    print("Base de données absente, initialisation et seeding...")
    from database.seed import seed_database
    seed_database()

# Instancier les services
valuation_service = ValuationService()
analytics_service = AnalyticsService()

# Entraîner le modèle prédictif au démarrage de l'application
try:
    valuation_service.train_model()
except Exception as e:
    print(f"Avertissement lors de l'entraînement du modèle prédictif : {e}")

# ==========================================
# ROUTES DES PAGES WEB (HTML RENDER)
# ==========================================

@app.route('/')
def index():
    """Page d'accueil de la plateforme Ymmo."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Récupérer les 3 derniers biens immobiliers disponibles pour la vitrine
    cursor.execute("""
        SELECT p.*, a.name as agency_name 
        FROM properties p
        JOIN agencies a ON p.agency_id = a.id
        WHERE p.status = 'available'
        ORDER BY p.id DESC
        LIMIT 3
    """)
    recent_properties = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return render_template('index.html', properties=recent_properties)

@app.route('/search')
def search():
    """Page de catalogue et recherche multicritères des biens."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Récupérer la liste des villes uniques dispos en catalogue pour les filtres
    cursor.execute("SELECT DISTINCT city FROM properties WHERE status='available' ORDER BY city ASC")
    cities = [r['city'] for r in cursor.fetchall()]
    conn.close()
    
    return render_template('search.html', cities=cities)

@app.route('/estimation')
def estimation():
    """Page publique d'estimation IA de bien immobilier."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Liste des villes pour le formulaire
    cursor.execute("SELECT DISTINCT city FROM agencies ORDER BY city ASC")
    cities = [r['city'] for r in cursor.fetchall()]
    conn.close()
    
    # Infos sur la précision du modèle IA pour la transparence et le jury
    model_stats = {
        "r2": round(valuation_service.r2_score * 100, 2),
        "mae": round(valuation_service.mae, 0),
        "is_trained": valuation_service.is_trained
    }
    
    return render_template('estimation.html', cities=cities, stats=model_stats)

@app.route('/dashboard')
def dashboard():
    """Page de tableau de bord commercial et management (sécurisée)."""
    if not session.get('agent_id'):
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion pour l'espace professionnel."""
    if session.get('agent_id'):
        return redirect(url_for('dashboard'))
        
    error = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '') # on ne valide pas le mot de passe dans cette démo mais on pourrait
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM agents WHERE LOWER(email) = ?", (email,))
        agent = cursor.fetchone()
        conn.close()
        
        if agent:
            session['agent_id'] = agent['id']
            session['agent_name'] = agent['name']
            session['agent_role'] = agent['role']
            return redirect(url_for('dashboard'))
        else:
            error = "Identifiants incorrects ou compte conseiller inexistant."
            
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    """Déconnexion de l'espace professionnel."""
    session.clear()
    return redirect(url_for('index'))


@app.route('/docs')
def docs():
    """Page de documentation académique interactive (Livrable DEV)."""
    return render_template('docs.html')

# ==========================================
# ENDPOINTS DE L'API REST (AJAX / JSON)
# ==========================================

@app.route('/api/properties', methods=['GET'])
def api_get_properties():
    """API pour l'affichage et filtrage dynamique des biens en catalogue."""
    city = request.args.get('city')
    prop_type = request.args.get('type')
    max_price = request.args.get('max_price', type=float)
    min_surface = request.args.get('min_surface', type=float)
    rooms = request.args.get('rooms', type=int)
    
    query = """
        SELECT p.*, a.name as agency_name, ag.name as agent_name, ag.phone as agent_phone, ag.email as agent_email
        FROM properties p
        JOIN agencies a ON p.agency_id = a.id
        JOIN agents ag ON p.agent_id = ag.id
        WHERE p.status = 'available'
    """
    params = []
    
    if city:
        query += " AND p.city = ?"
        params.append(city)
    if prop_type:
        query += " AND p.type = ?"
        params.append(prop_type)
    if max_price:
        query += " AND p.price <= ?"
        params.append(max_price)
    if min_surface:
        query += " AND p.surface >= ?"
        params.append(min_surface)
    if rooms:
        query += " AND p.rooms >= ?"
        params.append(rooms)
        
    query += " ORDER BY p.id DESC"
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    properties = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(properties)

@app.route('/api/properties/<int:prop_id>', methods=['GET'])
def api_get_property_detail(prop_id):
    """API pour obtenir les détails complets d'un bien immobilier."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.*, a.name as agency_name, a.city as agency_city, 
               ag.name as agent_name, ag.email as agent_email, ag.phone as agent_phone
        FROM properties p
        JOIN agencies a ON p.agency_id = a.id
        JOIN agents ag ON p.agent_id = ag.id
        WHERE p.id = ?
    """, (prop_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return jsonify({"error": "Bien introuvable"}), 404
        
    return jsonify(dict(row))

@app.route('/api/estimate', methods=['POST'])
def api_estimate_price():
    """API d'estimation de prix de bien immobilier par le moteur IA."""
    data = request.get_json() or {}
    
    try:
        surface = float(data.get('surface', 0))
        rooms = int(data.get('rooms', 0))
        bedrooms = int(data.get('bedrooms', 0))
        age = int(data.get('age', 0))
        city = data.get('city', '')
        prop_type = data.get('type', '')
        
        if surface <= 0 or rooms <= 0 or not city or not prop_type:
            return jsonify({"error": "Paramètres obligatoires manquants ou invalides"}), 400
            
        estimated_price = valuation_service.estimate_price(
            surface=surface, 
            rooms=rooms, 
            bedrooms=bedrooms, 
            age=age, 
            city=city, 
            prop_type=prop_type
        )
        
        # Récupérer le tarif moyen de m² dans cette ville pour info comparative
        city_m2_avg = valuation_service.city_avg_m2.get(city, 3500)
        
        return jsonify({
            "estimated_price": estimated_price,
            "estimated_price_m2": round(estimated_price / surface, 0),
            "city_average_m2": round(city_m2_avg, 0),
            "r2_score": round(valuation_service.r2_score * 100, 2),
            "mae": round(valuation_service.mae, 0)
        })
        
    except ValueError as e:
        return jsonify({"error": f"Format des entrées incorrect : {e}"}), 400
    except Exception as e:
        return jsonify({"error": f"Erreur lors de l'estimation : {e}"}), 500

@app.route('/api/leads', methods=['POST'])
def api_submit_lead():
    """API pour soumettre un formulaire de contact (génération de lead commercial)."""
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    message = data.get('message', '').strip()
    property_id = data.get('property_id')
    
    if not name or not email or not phone or not message:
        return jsonify({"error": "Tous les champs sont requis"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO leads (name, email, phone, message, property_id, status)
            VALUES (?, ?, ?, ?, ?, 'pending')
        """, (name, email, phone, message, property_id))
        conn.commit()
        lead_id = cursor.lastrowid
        return jsonify({"success": "Votre demande a bien été transmise à notre commercial !", "lead_id": lead_id}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Erreur lors de la soumission : {e}"}), 500
    finally:
        conn.close()

@app.route('/api/dashboard/stats', methods=['GET'])
def api_dashboard_stats():
    """API d'extraction globale de toutes les statistiques pour le tableau de bord interactif."""
    if not session.get('agent_id'):
        return jsonify({"error": "Accès non autorisé"}), 401
    try:
        general_stats = analytics_service.get_general_stats()
        sales_by_city = analytics_service.get_sales_by_city()
        sales_by_type = analytics_service.get_sales_by_type()
        sales_trends = analytics_service.get_sales_trends()
        top_agencies = analytics_service.get_top_agencies()
        top_agents = analytics_service.get_top_agents()
        hot_zones = analytics_service.get_hot_zones_recommendations()
        
        return jsonify({
            "general": general_stats,
            "by_city": sales_by_city,
            "by_type": sales_by_type,
            "trends": sales_trends,
            "top_agencies": top_agencies,
            "top_agents": top_agents,
            "hot_zones": hot_zones
        })
    except Exception as e:
        return jsonify({"error": f"Erreur lors du calcul des statistiques : {e}"}), 500

@app.route('/api/dashboard/leads', methods=['GET', 'POST'])
def api_dashboard_leads():
    """API pour lister et mettre à jour le statut des leads commerciaux."""
    if not session.get('agent_id'):
        return jsonify({"error": "Accès non autorisé"}), 401
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'GET':
        cursor.execute("""
            SELECT l.*, p.title as property_title, p.city as property_city
            FROM leads l
            LEFT JOIN properties p ON l.property_id = p.id
            ORDER BY l.id DESC
        """)
        leads = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(leads)
        
    elif request.method == 'POST':
        # Mettre à jour le statut d'un lead
        data = request.get_json() or {}
        lead_id = data.get('lead_id')
        new_status = data.get('status')
        
        if not lead_id or new_status not in ['pending', 'contacted', 'completed']:
            conn.close()
            return jsonify({"error": "Paramètres de mise à jour invalides"}), 400
            
        try:
            cursor.execute("UPDATE leads SET status = ? WHERE id = ?", (new_status, lead_id))
            conn.commit()
            conn.close()
            return jsonify({"success": "Statut du prospect mis à jour avec succès"})
        except Exception as e:
            conn.rollback()
            conn.close()
            return jsonify({"error": f"Erreur de mise à jour : {e}"}), 500

if __name__ == '__main__':
    # Activer le mode debug en local pour faciliter le développement
    app.run(debug=True, host='0.0.0.0', port=5000)
