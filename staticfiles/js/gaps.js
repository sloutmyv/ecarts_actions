/**
 * JavaScript pour la gestion des écarts
 */

// Gestion des modales HTMX
document.body.addEventListener('htmx:afterSwap', function(evt) {
    if (evt.detail.target.id === 'modal-container') {
        // Ouvrir la modale après chargement du contenu
        const modal = document.querySelector('#gap-report-modal');
        if (modal) {
            modal.classList.remove('hidden');
        }
    }
});

// Gestion des erreurs HTMX
document.body.addEventListener('htmx:responseError', function(evt) {
    console.error('Erreur HTMX:', evt.detail);
});

// Gestion des erreurs pour les requêtes HTMX
document.body.addEventListener('htmx:afterRequest', function(evt) {
    const xhr = evt.detail.xhr;
    if (xhr.status === 200) {
        try {
            const response = JSON.parse(xhr.responseText);
            if (response.error) {
                alert('Erreur: ' + response.error);
            }
        } catch (e) {
            // Pas une réponse JSON, comportement normal (HX-Redirect)
        }
    }
});

// Fonction pour fermer les modales
function closeModal() {
    const modal = document.querySelector('#gap-report-modal');
    if (modal) {
        modal.classList.add('hidden');
        document.querySelector('#modal-container').innerHTML = '';
    }
}

// Fermer la modale avec Escape
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeModal();
    }
});

// Rendre la fonction accessible globalement
window.closeModal = closeModal;