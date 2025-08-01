/**
 * JavaScript pour la gestion des utilisateurs
 * Gère les modales, les notifications et les interactions HTMX
 */

// Fonction pour fermer les modales
function closeModal() {
    const modals = document.querySelectorAll('[id$="-modal"]');
    modals.forEach(modal => {
        modal.classList.add('hidden');
        // Nettoyer le contenu après fermeture
        setTimeout(() => {
            modal.remove();
        }, 300);
    });
}

// Fermer les modales avec la touche Escape
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeModal();
    }
});

// Fermer les modales en cliquant en dehors
document.addEventListener('click', function(event) {
    const modals = document.querySelectorAll('[id$="-modal"]');
    modals.forEach(modal => {
        if (event.target === modal) {
            closeModal();
        }
    });
});

// Gestion des événements HTMX
document.addEventListener('htmx:afterRequest', function(event) {
    const response = event.detail.xhr;
    
    // Si la réponse contient une redirection réussie
    if (response.status === 200) {
        try {
            const data = JSON.parse(response.responseText);
            if (data.success && data.redirect) {
                // Fermer la modale et rediriger
                closeModal();
                window.location.href = data.redirect;
            }
        } catch (e) {
            // Si ce n'est pas du JSON, laisser HTMX gérer normalement
        }
    }
});

// Gestion des événements HTMX personnalisés
document.body.addEventListener('userDeleted', function(event) {
    console.log('Utilisateur supprimé avec succès');
    // Recharger la page pour refléter les changements
    location.reload();
});

// Auto-focus sur le premier champ des formulaires modaux
document.addEventListener('htmx:afterSettle', function(event) {
    const firstInput = event.target.querySelector('input:not([type="hidden"]):first-of-type');
    if (firstInput) {
        setTimeout(() => {
            firstInput.focus();
        }, 100);
    }
});

// Validation côté client pour le format du matricule
document.addEventListener('input', function(event) {
    if (event.target.name === 'matricule') {
        const value = event.target.value.toUpperCase();
        event.target.value = value;
        
        // Validation du pattern
        const pattern = /^[A-Z][0-9]{4}$/;
        const isValid = pattern.test(value) || value === '';
        
        // Styling conditionnel
        if (isValid) {
            event.target.classList.remove('border-red-500');
            event.target.classList.add('border-gray-300');
        } else if (value.length > 0) {
            event.target.classList.remove('border-gray-300');
            event.target.classList.add('border-red-500');
        }
    }
});

// Animation des notifications
document.addEventListener('htmx:afterSettle', function(event) {
    // Trouver toutes les nouvelles notifications
    const notifications = document.querySelectorAll('[class*="fixed top-4 right-4"]');
    notifications.forEach(notification => {
        // Animer l'entrée
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
            notification.style.transition = 'transform 0.3s ease-in-out';
        }, 10);
    });
});

console.log('Users.js loaded successfully');