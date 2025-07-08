// Script principal pour la page des conversations
document.addEventListener('DOMContentLoaded', function() {
    // Initialiser les conversations existantes si elles n'existent pas
    initializeDefaultConversations();
    
    // Charger et afficher les conversations
    ConversationUtils.refreshConversationsDisplay();
    
    // Initialiser la recherche
    initializeSearch();
    
    // Mettre à jour les dates toutes les minutes
    setInterval(updateRelativeDates, 60000);
});

// Fonction pour initialiser les conversations par défaut
function initializeDefaultConversations() {
    let conversations = ConversationUtils.loadConversations();
    
    // Si aucune conversation n'existe, créer des exemples
    if (conversations.length === 0) {
        const defaultConversations = [
            {
                id: 1,
                title: "Titre 1",
                date: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(), // Hier
                avatarColor: "#f97316",
                avatar: "🐻"
            },
            {
                id: 2,
                title: "Titre 2", 
                date: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(), // Il y a 3 jours
                avatarColor: "#ef4444",
                avatar: "🐻"
            },
            {
                id: 3,
                title: "Titre 3",
                date: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(), // Il y a 10 jours
                avatarColor: "#10b981",
                avatar: "🐻"
            }
        ];
        
        ConversationUtils.saveConversations(defaultConversations);
    }
}

// Fonction pour initialiser la recherche
function initializeSearch() {
    const searchInput = document.getElementById('conversationSearch');
    const clearButton = document.getElementById('clearSearch');

    if (!searchInput || !clearButton) return;

    // Événement de recherche
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase().trim();
        
        // Afficher/masquer le bouton clear
        clearButton.style.display = searchTerm.length > 0 ? 'block' : 'none';
        
        // Filtrer les conversations
        filterConversations(searchTerm);
    });

    // Événement clear
    clearButton.addEventListener('click', function() {
        searchInput.value = '';
        clearButton.style.display = 'none';
        filterConversations('');
        searchInput.focus();
    });
}

// Fonction pour filtrer les conversations
function filterConversations(searchTerm) {
    const conversationItems = document.querySelectorAll('.conversation-item');
    
    conversationItems.forEach(item => {
        const title = item.querySelector('.conversation-title').textContent.toLowerCase();
        const date = item.querySelector('.conversation-date').textContent.toLowerCase();
        
        if (searchTerm === '' || title.includes(searchTerm) || date.includes(searchTerm)) {
            item.style.display = 'flex';
            item.style.opacity = '1';
        } else {
            item.style.display = 'none';
            item.style.opacity = '0';
        }
    });
}

// Fonction pour mettre à jour les dates relatives
function updateRelativeDates() {
    const conversationItems = document.querySelectorAll('.conversation-item');
    
    conversationItems.forEach(item => {
        const dateElement = item.querySelector('.conversation-date');
        const isoDate = item.dataset.date;
        
        if (isoDate && dateElement) {
            const newRelativeDate = ConversationUtils.formatRelativeDate(isoDate);
            dateElement.textContent = newRelativeDate;
        }
    });
}

// Fonction pour créer une nouvelle conversation (appelée depuis le menu)
function createNewConversation(title) {
    const colors = ['#f97316', '#ef4444', '#10b981', '#8b5cf6', '#06b6d4', '#f59e0b'];
    const avatars = ['🐻', '🦊', '🐱', '🐶', '🐺', '🦁'];
    
    const randomColor = colors[Math.floor(Math.random() * colors.length)];
    const randomAvatar = avatars[Math.floor(Math.random() * avatars.length)];
    
    const conversations = ConversationUtils.loadConversations();
    const newConversation = {
        id: Date.now(),
        title: title,
        date: new Date().toISOString(),
        avatarColor: randomColor,
        avatar: randomAvatar
    };
    
    conversations.push(newConversation);
    ConversationUtils.saveConversations(conversations);
    ConversationUtils.refreshConversationsDisplay();
    
    // Faire défiler vers le haut pour voir la nouvelle conversation
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Fonction pour supprimer une conversation
function deleteConversationById(id) {
    const conversations = ConversationUtils.loadConversations();
    const filteredConversations = conversations.filter(conv => conv.id !== id);
    ConversationUtils.saveConversations(filteredConversations);
    ConversationUtils.refreshConversationsDisplay();
}

// Fonction pour ouvrir une conversation
function openConversation(conversationId) {
    console.log('Opening conversation with ID:', conversationId);
    // Ici tu peux rediriger vers la page de chat avec l'ID de la conversation
    // window.location.href = `/chat/${conversationId}`;
}

// Exposer les fonctions globalement pour le menu React
window.ConversationPageUtils = {
    createNewConversation,
    deleteConversationById,
    openConversation,
    updateRelativeDates
};