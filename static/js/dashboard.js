/* ==========================================================================
   AGENT DASHBOARD LOGIC & VISUALIZATION - YMMO PLATFORM (ES6 JS)
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // Éléments DOM des KPIs
    const kpiVolume = document.getElementById('kpi-volume');
    const kpiTransactions = document.getElementById('kpi-transactions');
    const kpiActive = document.getElementById('kpi-active');
    const kpiLeads = document.getElementById('kpi-leads');
    
    // Éléments DOM des tableaux et listes
    const agenciesRanking = document.getElementById('agencies-ranking');
    const agentsRanking = document.getElementById('agents-ranking');
    const hotZonesList = document.getElementById('hot-zones-list');
    const leadsTableBody = document.getElementById('leads-table-body');
    
    // Variables pour les graphiques Chart.js
    let trendChart = null;
    let typeChart = null;
    
    // Charger toutes les données du dashboard au démarrage
    loadDashboardData();
    loadLeadsData();
    
    // ==========================================
    // REQUÊTES ET POPULATION DES DONNÉES
    // ==========================================
    
    function loadDashboardData() {
        fetch('/api/dashboard/stats')
            .then(res => res.json())
            .then(data => {
                populateKPIs(data.general);
                renderTrendsChart(data.trends);
                renderTypeChart(data.by_type);
                populateAgenciesRanking(data.top_agencies);
                populateAgentsRanking(data.top_agents);
                populateHotZones(data.hot_zones);
            })
            .catch(err => {
                console.error("Erreur d'extraction des stats dashboard:", err);
            });
    }
    
    function loadLeadsData() {
        if (!leadsTableBody) return;
        
        fetch('/api/dashboard/leads')
            .then(res => res.json())
            .then(leads => {
                renderLeadsTable(leads);
            })
            .catch(err => {
                console.error("Erreur d'extraction des leads:", err);
            });
    }
    
    /**
     * Remplit les cartes de KPI en haut de page.
     */
    function populateKPIs(general) {
        if (!kpiVolume) return;
        
        // Format de monnaie (ex: 4 250 000 €)
        const formattedVolume = new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(general.total_sales_volume);
        
        kpiVolume.textContent = formattedVolume;
        kpiTransactions.textContent = general.total_transactions.toLocaleString();
        kpiActive.textContent = general.active_properties.toLocaleString();
        kpiLeads.textContent = general.pending_leads.toLocaleString();
    }
    
    /**
     * Génère la courbe de tendance mensuelle des ventes (Line Chart).
     */
    function renderTrendsChart(trends) {
        const ctx = document.getElementById('trendsChart');
        if (!ctx) return;
        
        const labels = trends.map(t => t.month_label);
        const dataValues = trends.map(t => t.monthly_revenue);
        
        // Configurer les couleurs selon le mode sombre ou clair
        const isLight = document.body.classList.contains('light-theme');
        const textColor = isLight ? '#1e293b' : '#008890';
        const gridColor = isLight ? 'rgba(30, 41, 59, 0.08)' : 'rgba(0, 136, 144, 0.08)';
        
        if (trendChart) trendChart.destroy();
        
        trendChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Volume de Ventes Mensuel (€)',
                    data: dataValues,
                    borderColor: '#735efa',
                    backgroundColor: 'rgba(115, 94, 250, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointBackgroundColor: '#735efa'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: textColor, font: { family: 'Inter', weight: 600 } }
                    }
                },
                scales: {
                    x: {
                        grid: { color: gridColor },
                        ticks: { color: textColor }
                    },
                    y: {
                        grid: { color: gridColor },
                        ticks: {
                            color: textColor,
                            callback: function(value) {
                                return (value / 1000).toLocaleString() + 'k €';
                            }
                        }
                    }
                }
            }
        });
    }
    
    /**
     * Génère la répartition par type de bien (Doughnut Chart).
     */
    function renderTypeChart(byType) {
        const ctx = document.getElementById('typeChart');
        if (!ctx) return;
        
        const labels = byType.map(t => t.type.toUpperCase());
        const dataValues = byType.map(t => t.sales_count);
        
        const isLight = document.body.classList.contains('light-theme');
        const textColor = isLight ? '#1e293b' : '#008890';
        
        if (typeChart) typeChart.destroy();
        
        typeChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: dataValues,
                    backgroundColor: [
                        'rgba(115, 94, 250, 0.75)', /* House - Deep Indigo */
                        'rgba(236, 72, 153, 0.75)',  /* Apartment - Pink */
                        'rgba(59, 130, 246, 0.75)',  /* Office - Blue */
                        'rgba(16, 185, 129, 0.75)'   /* Commercial - Emerald */
                    ],
                    borderColor: isLight ? '#ffffff' : '#0c101d',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { color: textColor, font: { family: 'Inter', weight: 600 } }
                    }
                }
            }
        });
    }
    
    /**
     * Remplit le classement des agences d'élite.
     */
    function populateAgenciesRanking(agencies) {
        if (!agenciesRanking) return;
        
        agenciesRanking.innerHTML = '';
        agencies.forEach((a, index) => {
            const tr = document.createElement('tr');
            const revenueFormatted = new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(a.total_revenue);
            
            tr.innerHTML = `
                <td><strong style="color: var(--accent-primary);">#${index + 1}</strong></td>
                <td><strong>${a.agency_name}</strong></td>
                <td>${a.city}</td>
                <td>${a.sales_count} ventes</td>
                <td style="text-align: right; font-weight: 700; color: var(--accent-success);">${revenueFormatted}</td>
            `;
            agenciesRanking.appendChild(tr);
        });
    }
    
    /**
     * Remplit le palmarès des commerciaux.
     */
    function populateAgentsRanking(agents) {
        if (!agentsRanking) return;
        
        agentsRanking.innerHTML = '';
        agents.forEach((a, index) => {
            const tr = document.createElement('tr');
            const revenueFormatted = new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(a.total_revenue);
            
            tr.innerHTML = `
                <td><strong style="color: var(--accent-secondary);">#${index + 1}</strong></td>
                <td>👤 <strong>${a.agent_name}</strong></td>
                <td>${a.agency_name}</td>
                <td>${a.sales_count} ventes</td>
                <td style="text-align: right; font-weight: 700; color: var(--accent-success);">${revenueFormatted}</td>
            `;
            agentsRanking.appendChild(tr);
        });
    }
    
    /**
     * Affiche les opportunités de marché identifiées (Hot Zones).
     */
    function populateHotZones(zones) {
        if (!hotZonesList) return;
        
        hotZonesList.innerHTML = '';
        zones.forEach(z => {
            const card = document.createElement('div');
            card.className = 'glass-panel';
            card.style.padding = '1.25rem';
            card.style.borderRadius = 'var(--radius-sm)';
            
            card.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <span class="status-badge status-completed" style="font-size: 0.7rem; text-transform: uppercase;">${z.type}</span>
                    <strong style="color: var(--accent-success);">${z.metric}</strong>
                </div>
                <h4 style="margin: 0 0 0.5rem 0; font-size: 1.05rem;">${z.title}</h4>
                <p style="opacity: 0.75; font-size: 0.85rem; margin: 0;">${z.description}</p>
            `;
            hotZonesList.appendChild(card);
        });
    }
    
    /**
     * Construit et gère la liste dynamique des prospects clients (leads).
     */
    function renderLeadsTable(leads) {
        if (!leadsTableBody) return;
        
        leadsTableBody.innerHTML = '';
        
        if (leads.length === 0) {
            leadsTableBody.innerHTML = `
                <tr>
                    <td colspan="6" style="text-align: center; padding: 3rem; opacity: 0.7;">Aucune demande de prospect enregistrée actuellement.</td>
                </tr>
            `;
            return;
        }
        
        leads.forEach(l => {
            const tr = document.createElement('tr');
            
            // Choisir la classe selon le statut
            let statusClass = 'status-pending';
            if (l.status === 'contacted') statusClass = 'status-contacted';
            if (l.status === 'completed') statusClass = 'status-completed';
            
            tr.innerHTML = `
                <td>
                    <strong>${l.name}</strong><br>
                    <span style="font-size: 0.8rem; opacity: 0.7;">✉️ ${l.email}</span><br>
                    <span style="font-size: 0.8rem; opacity: 0.7;">📞 ${l.phone}</span>
                </td>
                <td>
                    <a href="/search?id=${l.property_id}" target="_blank" style="color: var(--accent-primary-hover); text-decoration: underline;">
                        ${l.property_title || 'Bien d\'archive'}
                    </a><br>
                    <span style="font-size: 0.8rem; opacity: 0.6;">📍 Ville : ${l.property_city || 'Inconnue'}</span>
                </td>
                <td style="max-width: 250px; font-size: 0.88rem; opacity: 0.9;">
                    <p style="margin: 0; white-space: pre-line;">"${l.message}"</p>
                </td>
                <td>
                    <span style="font-size: 0.8rem; opacity: 0.7;">${new Date(l.created_at).toLocaleDateString('fr-FR')}</span>
                </td>
                <td>
                    <select class="filter-control lead-status-select" data-id="${l.id}" style="font-size: 0.8rem; padding: 0.4rem 0.6rem; width: auto;">
                        <option value="pending" ${l.status === 'pending' ? 'selected' : ''}>⏳ À recontacter</option>
                        <option value="contacted" ${l.status === 'contacted' ? 'selected' : ''}>📞 En cours</option>
                        <option value="completed" ${l.status === 'completed' ? 'selected' : ''}>✅ Traité</option>
                    </select>
                </td>
            `;
            
            leadsTableBody.appendChild(tr);
        });
        
        // Attacher les écouteurs de changement de statut
        document.querySelectorAll('.lead-status-select').forEach(select => {
            select.addEventListener('change', (e) => {
                const leadId = e.target.getAttribute('data-id');
                const newStatus = e.target.value;
                updateLeadStatus(leadId, newStatus);
            });
        });

        // Initialiser les dropdowns personnalisés sur les selects nouvellement ajoutés
        if (typeof initCustomSelects === 'function') {
            initCustomSelects();
        }
    }
    
    /**
     * Envoie une requête POST d'action commerciale pour changer le statut du prospect.
     */
    function updateLeadStatus(leadId, newStatus) {
        fetch('/api/dashboard/leads', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ lead_id: parseInt(leadId), status: newStatus })
        })
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                alert(`⚠️ Erreur : ${data.error}`);
            } else {
                // Rafraîchir les KPIs et la liste proprement sans recharger
                loadDashboardData();
            }
        })
        .catch(err => {
            console.error("Erreur de mise à jour lead:", err);
            alert("⚠️ Erreur réseau, impossible de mettre à jour le statut.");
        });
    }
    
    // Réinitialiser les graphiques si l'utilisateur change de thème (pour adapter les couleurs)
    const themeBtn = document.getElementById('theme-toggle');
    if (themeBtn) {
        themeBtn.addEventListener('click', () => {
            setTimeout(() => {
                loadDashboardData();
            }, 150);
        });
    }

    // ==========================================
    // AJOUT DE BIENS IMMOBILIERS (MODALE & FORM)
    // ==========================================
    const addPropertyModal = document.getElementById('add-property-modal');
    const btnAddProperty = document.getElementById('btn-add-property');
    const addPropertyClose = document.getElementById('add-property-modal-close');
    const addPropertyForm = document.getElementById('add-property-form');
    const addPropertyStatusMsg = document.getElementById('add-property-status-msg');

    if (btnAddProperty && addPropertyModal) {
        // Ouvrir la modale
        btnAddProperty.addEventListener('click', () => {
            addPropertyModal.classList.add('active');
            document.body.style.overflow = 'hidden';
            if (addPropertyStatusMsg) {
                addPropertyStatusMsg.style.display = 'none';
                addPropertyStatusMsg.textContent = '';
            }
        });

        // Fermer la modale
        const closeAddPropertyModal = () => {
            addPropertyModal.classList.remove('active');
            document.body.style.overflow = '';
            addPropertyForm.reset();
        };

        if (addPropertyClose) {
            addPropertyClose.addEventListener('click', closeAddPropertyModal);
        }

        addPropertyModal.addEventListener('click', (e) => {
            if (e.target === addPropertyModal) closeAddPropertyModal();
        });

        // Accessibilité Échap
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && addPropertyModal.classList.contains('active')) {
                closeAddPropertyModal();
            }
        });

        // Soumission du formulaire
        if (addPropertyForm) {
            addPropertyForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const submitBtn = addPropertyForm.querySelector('button[type="submit"]');
                
                // Désactiver le bouton pendant le traitement
                submitBtn.disabled = true;
                submitBtn.textContent = 'Enregistrement en cours...';

                if (addPropertyStatusMsg) {
                    addPropertyStatusMsg.style.display = 'none';
                    addPropertyStatusMsg.textContent = '';
                }

                // Récupérer les données du formulaire
                const formData = new FormData(addPropertyForm);
                const payload = {
                    title: formData.get('title'),
                    type: formData.get('type'),
                    description: formData.get('description'),
                    price: parseFloat(formData.get('price')),
                    surface: parseFloat(formData.get('surface')),
                    year_built: formData.get('year_built') ? parseInt(formData.get('year_built')) : null,
                    rooms: parseInt(formData.get('rooms')),
                    bedrooms: parseInt(formData.get('bedrooms')),
                    city: formData.get('city'),
                    zip_code: formData.get('zip_code'),
                    agency_id: parseInt(formData.get('agency_id')),
                    address: formData.get('address'),
                    image_url: formData.get('image_url') || null
                };

                fetch('/api/properties', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                })
                .then(res => res.json())
                .then(data => {
                    if (data.error) {
                        if (addPropertyStatusMsg) {
                            addPropertyStatusMsg.style.color = '#ef4444';
                            addPropertyStatusMsg.textContent = `❌ ${data.error}`;
                            addPropertyStatusMsg.style.display = 'block';
                        }
                        submitBtn.disabled = false;
                        submitBtn.textContent = 'Enregistrer le bien immobilier';
                    } else {
                        if (addPropertyStatusMsg) {
                            addPropertyStatusMsg.style.color = '#10b981';
                            addPropertyStatusMsg.textContent = `✅ ${data.success}`;
                            addPropertyStatusMsg.style.display = 'block';
                        }
                        // Actualiser les statistiques globales du dashboard
                        loadDashboardData();
                        
                        // Fermer la modale après un court délai
                        setTimeout(() => {
                            closeAddPropertyModal();
                            submitBtn.disabled = false;
                            submitBtn.textContent = 'Enregistrer le bien immobilier';
                        }, 2000);
                    }
                })
                .catch(err => {
                    console.error("Erreur lors de l'ajout du bien:", err);
                    if (addPropertyStatusMsg) {
                        addPropertyStatusMsg.style.color = '#ef4444';
                        addPropertyStatusMsg.textContent = "⚠️ Erreur réseau, impossible d'enregistrer le bien.";
                        addPropertyStatusMsg.style.display = 'block';
                    }
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Enregistrer le bien immobilier';
                });
            });
        }
    }
});
