/* ==========================================================================
   CLIENT INTERACTION & API CONNECTIVITY - YMMO PLATFORM (ES6 JS)
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // Éléments du DOM (Recherche & Filtres)
    const propertiesGrid = document.getElementById('properties-grid');
    const filterCity = document.getElementById('filter-city');
    const filterType = document.getElementById('filter-type');
    const filterMaxPrice = document.getElementById('filter-max-price');
    const filterMinSurface = document.getElementById('filter-min-surface');
    const filterRooms = document.getElementById('filter-rooms');
    const resetFiltersBtn = document.getElementById('reset-filters');
    
    // Éléments de la Modale de Détails & Contact
    const detailModal = document.getElementById('detail-modal');
    const modalClose = document.getElementById('modal-close');
    const contactForm = document.getElementById('contact-form');
    
    // Si la grille de propriétés est présente sur la page actuelle, on initialise les événements
    if (propertiesGrid) {
        // Initialiser la recherche
        fetchProperties();
        
        // Attacher les écouteurs sur les filtres
        [filterCity, filterType, filterMaxPrice, filterMinSurface, filterRooms].forEach(element => {
            if (element) {
                element.addEventListener('change', () => fetchProperties());
                element.addEventListener('input', debounce(() => fetchProperties(), 400));
            }
        });
        
        if (resetFiltersBtn) {
            resetFiltersBtn.addEventListener('click', () => {
                if (filterCity) filterCity.value = '';
                if (filterType) filterType.value = '';
                if (filterMaxPrice) filterMaxPrice.value = '';
                if (filterMinSurface) filterMinSurface.value = '';
                if (filterRooms) filterRooms.value = '';
                fetchProperties();
            });
        }
    }
    
    // Gestion de la fermeture de la modale
    if (modalClose) {
        modalClose.addEventListener('click', closePropertyModal);
        detailModal.addEventListener('click', (e) => {
            if (e.target === detailModal) closePropertyModal();
        });
        
        // Fermeture avec la touche Échap pour l'accessibilité
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && detailModal.classList.contains('active')) {
                closePropertyModal();
            }
        });
    }
    
    // Gestion du formulaire de contact commercial (Lead)
    if (contactForm) {
        contactForm.addEventListener('submit', handleLeadFormSubmit);
    }
    
    // Vérifier si un ID de propriété spécifique est passé en URL pour l'ouvrir immédiatement
    const urlParams = new URLSearchParams(window.location.search);
    const propId = urlParams.get('id');
    if (propId && propertiesGrid) {
        openPropertyModal(propId);
    }
    
    // ==========================================
    // MÉTHODES DE TRAITEMENT ET DE REQUÊTES
    // ==========================================
    
    /**
     * Récupère la liste filtrée des biens immobiliers auprès de l'API Flask.
     */
    function fetchProperties() {
        if (!propertiesGrid) return;
        
        // Afficher un loader CSS
        propertiesGrid.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 4rem;">
                <div class="loader-spinner" style="display: inline-block; width: 50px; height: 50px; border: 4px solid var(--border-dark); border-top-color: var(--accent-primary); border-radius: 50%; animation: spin 1s linear infinite;"></div>
                <p style="margin-top: 1rem; opacity: 0.7;">Chargement des opportunités Ymmo...</p>
            </div>
        `;
        
        // Construire les paramètres de requête
        const queryParams = new URLSearchParams();
        if (filterCity && filterCity.value) queryParams.append('city', filterCity.value);
        if (filterType && filterType.value) queryParams.append('type', filterType.value);
        if (filterMaxPrice && filterMaxPrice.value) queryParams.append('max_price', filterMaxPrice.value);
        if (filterMinSurface && filterMinSurface.value) queryParams.append('min_surface', filterMinSurface.value);
        if (filterRooms && filterRooms.value) queryParams.append('rooms', filterRooms.value);
        
        fetch(`/api/properties?${queryParams.toString()}`)
            .then(res => res.json())
            .then(data => {
                renderPropertyCards(data);
            })
            .catch(err => {
                console.error("Erreur d'extraction des biens:", err);
                propertiesGrid.innerHTML = `
                    <div style="grid-column: 1/-1; text-align: center; padding: 4rem; color: #ef4444;">
                        <p>⚠️ Erreur réseau : impossible de contacter l'API Ymmo. Veuillez réessayer.</p>
                    </div>
                `;
            });
    }
    
    /**
     * Construit et affiche les cartes HTML pour chaque bien immobilier.
     */
    function renderPropertyCards(properties) {
        if (!propertiesGrid) return;
        
        if (properties.length === 0) {
            propertiesGrid.innerHTML = `
                <div style="grid-column: 1/-1; text-align: center; padding: 5rem;" class="glass-panel">
                    <h3 style="margin-bottom: 0.5rem;">Aucun bien correspondant</h3>
                    <p style="opacity: 0.7;">Nous vous suggérons d'élargir vos critères de recherche ou de tester une autre ville.</p>
                </div>
            `;
            return;
        }
        
        propertiesGrid.innerHTML = '';
        
        properties.forEach((prop, index) => {
            const card = document.createElement('article');
            card.className = 'property-card';
            card.id = `prop-card-${prop.id}`;
            card.style.opacity = '0';
            card.style.transform = 'translateY(15px)';
            
            // Format du prix (ex: 245 000)
            const formattedPrice = new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(prop.price);
            
            card.innerHTML = `
                <img class="property-img" src="${prop.image_url || 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=800&q=80'}" alt="${prop.title}">
                <div class="property-content">
                    <span class="property-badge badge-${prop.type}">${prop.type}</span>
                    <h3 class="property-title">${prop.title}</h3>
                    <p style="opacity: 0.7; font-size: 0.88rem; margin-bottom: 1.2rem;">📍 ${prop.city} (${prop.zip_code})</p>
                    <div class="property-price">${formattedPrice}</div>
                    <div class="property-features">
                        <span>📐 ${prop.surface} m²</span>
                        <span>🚪 ${prop.rooms} p.</span>
                        <span>🛏️ ${prop.bedrooms} ch.</span>
                    </div>
                    <button class="btn btn-secondary view-details-btn" data-id="${prop.id}" style="margin-top: 1.25rem; font-size: 0.85rem; padding: 0.6rem 0;" aria-label="Voir les détails de ${prop.title}">Voir les détails</button>
                </div>
            `;
            
            propertiesGrid.appendChild(card);
            
            // Animation d'entrée progressive (effet de cascade fluide)
            setTimeout(() => {
                card.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 40);
        });
        
        // Attacher les clics aux boutons de détails
        document.querySelectorAll('.view-details-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.target.getAttribute('data-id');
                openPropertyModal(id);
            });
        });
    }
    
    /**
     * Ouvre la modale et charge les informations spécifiques du bien par appel d'API.
     */
    function openPropertyModal(id) {
        if (!detailModal) return;
        
        // Afficher l'overlay avec un loader d'attente
        detailModal.classList.add('active');
        document.body.style.overflow = 'hidden'; // Bloquer le défilement arrière
        
        const container = document.getElementById('modal-inner-content');
        container.innerHTML = `
            <div style="text-align: center; padding: 6rem 0;">
                <div class="loader-spinner" style="display: inline-block; width: 40px; height: 40px; border: 3px solid rgba(255,255,255,0.1); border-top-color: var(--accent-primary); border-radius: 50%; animation: spin 1s linear infinite;"></div>
                <p style="margin-top: 1rem; opacity: 0.7;">Chargement de l'annonce d'exception...</p>
            </div>
        `;
        
        fetch(`/api/properties/${id}`)
            .then(res => {
                if (!res.ok) throw new Error("Erreur de récupération");
                return res.json();
            })
            .then(prop => {
                const formattedPrice = new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(prop.price);
                
                container.innerHTML = `
                    <div style="display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 2rem; margin-top: 1rem;">
                        <!-- Partie Gauche : Média & Descriptif -->
                        <div>
                            <img src="${prop.image_url || 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=800&q=80'}" alt="${prop.title}" style="width: 100%; height: 300px; object-fit: cover; border-radius: var(--radius-md); margin-bottom: 1.5rem; display: block; border: 1px solid var(--border-dark);">
                            <span class="property-badge badge-${prop.type}">${prop.type}</span>
                            <h2 style="margin: 0.5rem 0 1rem 0;">${prop.title}</h2>
                            <p style="opacity: 0.9; margin-bottom: 1.5rem; font-size: 0.95rem; white-space: pre-line;">${prop.description}</p>
                            
                            <h3 style="margin-bottom: 0.75rem;">Détails Techniques</h3>
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 1rem; margin-bottom: 1.5rem;">
                                <div class="glass-panel" style="padding: 1rem; text-align: center; border-radius: var(--radius-sm);">
                                    <div style="font-size: 0.8rem; opacity: 0.7;">Surface habitable</div>
                                    <strong style="font-size: 1.1rem;">${prop.surface} m²</strong>
                                </div>
                                <div class="glass-panel" style="padding: 1rem; text-align: center; border-radius: var(--radius-sm);">
                                    <div style="font-size: 0.8rem; opacity: 0.7;">Pièces de vie</div>
                                    <strong style="font-size: 1.1rem;">${prop.rooms} pièces</strong>
                                </div>
                                <div class="glass-panel" style="padding: 1rem; text-align: center; border-radius: var(--radius-sm);">
                                    <div style="font-size: 0.8rem; opacity: 0.7;">Chambres</div>
                                    <strong style="font-size: 1.1rem;">${prop.bedrooms} ch.</strong>
                                </div>
                                <div class="glass-panel" style="padding: 1rem; text-align: center; border-radius: var(--radius-sm);">
                                    <div style="font-size: 0.8rem; opacity: 0.7;">Année de construction</div>
                                    <strong style="font-size: 1.1rem;">${prop.year_built || 'Non renseignée'}</strong>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Partie Droite : Prix, Agence & Contact -->
                        <div style="display: flex; flex-direction: column; gap: 1.5rem;">
                            <div class="glass-panel" style="padding: 1.5rem; border-radius: var(--radius-md);">
                                <div style="font-size: 0.85rem; opacity: 0.7; margin-bottom: 0.25rem;">Prix de présentation FAI</div>
                                <div class="property-price" style="font-size: 2.2rem; margin-bottom: 0.5rem; font-weight: 800;">${formattedPrice}</div>
                                <div style="font-size: 0.8rem; opacity: 0.6;">Adresse : ${prop.address}, ${prop.zip_code} ${prop.city}</div>
                            </div>
                            
                            <div class="glass-panel" style="padding: 1.5rem; border-radius: var(--radius-md);">
                                <h4 style="margin-bottom: 0.75rem; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.8;">Conseiller en charge</h4>
                                <strong>👤 ${prop.agent_name}</strong>
                                <div style="font-size: 0.85rem; opacity: 0.7; margin-top: 0.25rem;">📍 Agence de rattachement : ${prop.agency_name}</div>
                                <div style="font-size: 0.85rem; opacity: 0.7; margin-top: 0.25rem;">📞 Téléphone : ${prop.agent_phone}</div>
                                <div style="font-size: 0.85rem; opacity: 0.7; margin-top: 0.25rem;">✉️ E-mail : ${prop.agent_email}</div>
                            </div>
                            
                            <!-- Formulaire de contact direct -->
                            <div class="glass-panel" style="padding: 1.5rem; border-radius: var(--radius-md);">
                                <h4 style="margin-bottom: 1rem; font-size: 0.95rem;">Contacter le conseiller par e-mail</h4>
                                <form id="modal-lead-form">
                                    <input type="hidden" name="property_id" value="${prop.id}">
                                    <div style="margin-bottom: 0.75rem;">
                                        <input class="filter-control" type="text" name="name" placeholder="Votre nom complet" required style="font-size: 0.85rem; padding: 0.6rem 0.8rem;">
                                    </div>
                                    <div style="margin-bottom: 0.75rem; display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;">
                                        <input class="filter-control" type="email" name="email" placeholder="Votre e-mail" required style="font-size: 0.85rem; padding: 0.6rem 0.8rem;">
                                        <input class="filter-control" type="tel" name="phone" placeholder="Votre téléphone" required style="font-size: 0.85rem; padding: 0.6rem 0.8rem;">
                                    </div>
                                    <div style="margin-bottom: 1rem;">
                                        <textarea class="filter-control" name="message" rows="3" placeholder="Bonjour, je souhaite visiter ce bien..." required style="font-size: 0.85rem; padding: 0.6rem 0.8rem; resize: none;"></textarea>
                                    </div>
                                    <button class="btn btn-primary" type="submit" style="width: 100%; font-size: 0.88rem; padding: 0.7rem 0;">Envoyer ma demande</button>
                                </form>
                                <div id="lead-status-msg" style="margin-top: 0.75rem; text-align: center; font-size: 0.85rem; display: none;"></div>
                            </div>
                        </div>
                    </div>
                `;
                
                // Ré-attacher l'écouteur de formulaire de lead dans la modale
                document.getElementById('modal-lead-form').addEventListener('submit', handleLeadFormSubmit);
            })
            .catch(err => {
                console.error("Détails introuvables:", err);
                container.innerHTML = `
                    <div style="text-align: center; padding: 4rem; color: #ef4444;">
                        <p>⚠️ Erreur réseau : impossible de charger les détails du bien.</p>
                    </div>
                `;
            });
    }
    
    /**
     * Ferme la modale de détails.
     */
    function closePropertyModal() {
        if (!detailModal) return;
        detailModal.classList.remove('active');
        document.body.style.overflow = ''; // Restaurer le défilement
        // Nettoyer l'URL
        window.history.replaceState({}, document.title, window.location.pathname);
    }
    
    /**
     * Gère la soumission du formulaire de contact commercial (Lead API).
     */
    function handleLeadFormSubmit(e) {
        e.preventDefault();
        const form = e.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        const statusMsg = document.getElementById('lead-status-msg') || document.createElement('div');
        
        if (!document.getElementById('lead-status-msg')) {
            statusMsg.id = 'lead-status-msg';
            statusMsg.style.marginTop = '0.75rem';
            statusMsg.style.textAlign = 'center';
            statusMsg.style.fontSize = '0.85rem';
            form.appendChild(statusMsg);
        }
        
        // Bloquer le bouton pendant l'envoi
        submitBtn.disabled = true;
        submitBtn.textContent = 'Transmission en cours...';
        
        const payload = {
            name: form.name.value,
            email: form.email.value,
            phone: form.phone.value,
            message: form.message.value,
            property_id: parseInt(form.property_id.value)
        };
        
        fetch('/api/leads', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                statusMsg.style.color = '#ef4444';
                statusMsg.textContent = `❌ ${data.error}`;
                submitBtn.disabled = false;
                submitBtn.textContent = 'Envoyer ma demande';
            } else {
                statusMsg.style.color = '#10b981';
                statusMsg.textContent = `✅ ${data.success}`;
                form.reset();
                setTimeout(() => {
                    closePropertyModal();
                }, 2500);
            }
            statusMsg.style.display = 'block';
        })
        .catch(err => {
            console.error("Erreur lead:", err);
            statusMsg.style.color = '#ef4444';
            statusMsg.textContent = "⚠️ Erreur réseau : impossible de transmettre.";
            submitBtn.disabled = false;
            submitBtn.textContent = 'Envoyer ma demande';
            statusMsg.style.display = 'block';
        });
    }
    
    // Helper pour éviter les appels d'API excessifs sur la saisie manuelle (Filtre par prix, etc.)
    function debounce(func, wait) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }
});

// Ajouter les keyframes de rotation de loader CSS au document de façon dynamique
const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);
