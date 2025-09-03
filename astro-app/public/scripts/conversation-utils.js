function getDisplayName(user) {
  // Si l'utilisateur a un prénom et un nom
  if (user.prenom && user.nom) {
      return `${user.prenom} ${user.nom}`;
  }
  // Si l'utilisateur a seulement un prénom
  else if (user.prenom) {
      return user.prenom;
  }
  // Si l'utilisateur a seulement un nom
  else if (user.nom) {
      return user.nom;
  }
  // Sinon, utiliser le début de l'email
  else {
      return user.email.split('@')[0];
  }
}

// Variable globale pour stocker les données utilisateur
let currentUser = null;

// Vérification d'authentification
async function checkAuth() {
    try {
        const response = await fetch('http://localhost:8080/auth/check', {
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (!data.authenticated) {
            // Pas connecté, rediriger vers la connexion
            window.location.href = '/connexion/connexion';
            return null;
        }
        
        // Stocker les données utilisateur globalement
        currentUser = data.user;
        return data.user;
        
    } catch (error) {
        console.error('Erreur vérification auth:', error);
        // En cas d'erreur, rediriger vers la connexion
        window.location.href = '/connexion/connexion';
        return null;
    }
}

// Fonction pour recup l'heure
function getGreeting() {
    const now = new Date();
    const hour = now.getHours();
    
    if (hour >= 6 && hour < 18) {
        return "Bonjour";
    } else {
        return "Bonsoir";
    }
}

// Fonction pour calculer l'âge à partir de la date de naissance
function calculateAge(birthdate) {
    const today = new Date();
    const birth = new Date(birthdate);
    
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    
    // Si on n'a pas encore eu l'anniversaire cette année
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
        age--;
    }
    
    return age;
}

// Fonction pour mettre à jour la salutation
async function updateGreeting() {
    const greetingElement = document.getElementById('dynamicGreeting');
    const greeting = getGreeting();
    
    if (!greetingElement) return;
    
    // Si on n'a pas encore les données utilisateur, les récupérer
    if (!currentUser) {
        const user = await checkAuth();
        if (!user) return; // Redirection effectuée dans checkAuth
    }
    
    // Maintenant on peut utiliser currentUser
    if (currentUser) {
        const username = getDisplayName(currentUser);
        console.log(username);
        greetingElement.textContent = `${greeting} ${username}`;
    } else {
        // Fallback si pas de données utilisateur
        greetingElement.textContent = greeting;
    }
}

async function updateAge() {
    const ageElement = document.getElementById('dynamicAge');
    if (!ageElement) return;

    // Récupération user si nécessaire
    if (!currentUser) {
        currentUser = await checkAuth();
        if (!currentUser) return;
    }

    let birthdate = currentUser.date_naissance;

    if (Array.isArray(birthdate)) {
        birthdate = birthdate[0];
    }

    // Pas de date → ne rien afficher
    if (!birthdate || birthdate.trim() === "") {
        ageElement.textContent = "";
        return;
    }

    // Vérifier que la date est valide
    const parsedDate = new Date(birthdate);
    if (isNaN(parsedDate.getTime())) {
        ageElement.textContent = "";
        return;
    }

    // Calculer l’âge
    const age = calculateAge(parsedDate);
    ageElement.textContent = age > 0 ? `${age} ans` : "";
}


// Mettre à jour la salutation et l'âge au chargement de la page
document.addEventListener('DOMContentLoaded', async function() {
    // Mettre à jour les informations utilisateur
    await updateGreeting();
    await updateAge();
});
// Mettre à jour la salutation toutes les minutes
setInterval(updateGreeting, 60000);

// Fonction pour garder les dates 
function formatRelativeDate(date) {
  const now = new Date();
  const conversationDate = new Date(date);
  
  const isToday = now.toDateString() === conversationDate.toDateString();
  
  if (isToday) {
    return "Aujourd'hui";
  }
  
  // Calculer la différence en jours
  const diffTime = Math.abs(now - conversationDate);
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
  
  if (diffDays === 1) {
    return "Hier";
  } else if (diffDays <= 6) {
    return `Il y a ${diffDays} jours`;
  } else if (diffDays === 7) {
    return `Il y a une semaine`;
  } else {
    // ssi plus de 7 jours
    const options = { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    };
    return conversationDate.toLocaleDateString('fr-FR', options);
  }
}

// trier les conversations
function sortConversations(conversations, sortType = 'date') {
  return conversations.sort((a, b) => {
    switch (sortType) {
      case 'date':
        return new Date(b.date) - new Date(a.date);
      case 'alphabetical':
        return a.title.localeCompare(b.title, 'fr', { sensitivity: 'base' });
      case 'oldest':
        return new Date(a.date) - new Date(b.date);
      default:
        return 0;
    }
  });
}

// créer une nouvelle conversation
function createConversation(title, avatarColor = '#f97316') {
  return {
    id: Date.now(),
    title: title,
    date: new Date().toISOString(),
    avatarColor: avatarColor,
    avatar: '🐻',
    bin: '🗑️'
  };
}

// sauvegarder les conversations dans le localStorage
function saveConversations(conversations) {
  localStorage.setItem('conversations', JSON.stringify(conversations));
}

// load les conversations depuis localStorage
function loadConversations() {
  const saved = localStorage.getItem('conversations');
  return saved ? JSON.parse(saved) : [];
}

// Supp une conversation
function deleteConversation(conversationId) {
  let conversations = loadConversations();
  conversations = conversations.filter(conv => conv.id !== conversationId);
  saveConversations(conversations);
  return conversations;
}

// génére le HTML d'une conversation **CHATGPT J'AURAI PAS SU FAIRE
function generateConversationHTML(conversation) {
  const relativeDate = formatRelativeDate(conversation.date);
  
  return `
    <div class="conversation-item" data-id="${conversation.id}" data-date="${conversation.date}" data-title="${conversation.title}">
      <div class="delete-background">🗑️</div>
      <div class="avatar">
        <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='50' fill='${encodeURIComponent(conversation.avatarColor)}'/%3E%3Ctext x='50' y='65' font-family='Arial' font-size='50' fill='white' text-anchor='middle'%3E${conversation.avatar}%3C/text%3E%3C/svg%3E" alt="Avatar" />
      </div>
      <div class="conversation-content">
        <div class="conversation-title">${conversation.title}</div>
        <div class="conversation-date">${relativeDate}</div>
      </div>
      <div class="bin-icon" data-id="${conversation.id}" title="Supprimer la conversation">
        ${conversation.bin || '🗑️'}
      </div>
    </div>
  `;
}

// Fonction pour attacher les listeners de swipe à un élément
function attachSwipeListeners(item) {
  let startX = 0;
  let currentX = 0;
  let isSwipeGesture = false;
  let activeItem = null;

  function handleStart(e) {
    activeItem = item;
    startX = e.type === 'mousedown' ? e.clientX : e.touches[0].clientX;
    isSwipeGesture = false;
    item.classList.add('swiping');
  }

  function handleMove(e) {
    if (!activeItem) return;

    e.preventDefault();
    currentX = e.type === 'mousemove' ? e.clientX : e.touches[0].clientX;
    const deltaX = currentX - startX;

    if (deltaX > 0) {
      isSwipeGesture = true;
      const moveDistance = Math.min(deltaX, 80);
      activeItem.style.transform = `translateX(${moveDistance}px)`;
      
      if (moveDistance > 40) {
        activeItem.classList.add('show-delete');
      } else {
        activeItem.classList.remove('show-delete');
      }
    }
  }

  function handleEnd(e) {
    if (!activeItem) return;

    const deltaX = currentX - startX;
    activeItem.classList.remove('swiping');

    if (deltaX > 60) {
      if (confirm('Supprimer cette conversation ?')) {
        const conversationId = parseInt(activeItem.dataset.id);
        deleteConversation(conversationId);
        activeItem.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
          refreshConversationsDisplay();
        }, 300);
      } else {
        activeItem.style.transform = 'translateX(0)';
        activeItem.classList.remove('show-delete');
      }
    } else {
      activeItem.style.transform = 'translateX(0)';
      activeItem.classList.remove('show-delete');
    }

    activeItem = null;
    startX = 0;
    currentX = 0;
    setTimeout(() => {
      isSwipeGesture = false;
    }, 10);
  }

  // Attacher les listeners
  item.addEventListener('mousedown', handleStart);
  document.addEventListener('mousemove', handleMove);
  document.addEventListener('mouseup', handleEnd);
  item.addEventListener('touchstart', handleStart, { passive: true });
  document.addEventListener('touchmove', handleMove, { passive: false });
  document.addEventListener('touchend', handleEnd);

  // ouvrir la conv
  item.addEventListener('click', function(e) {
    // Empêcher l'ouverture si on clique sur la poubelle
    if (e.target.classList.contains('bin-icon') || e.target.closest('.bin-icon')) {
      return;
    }
    
    if (!isSwipeGesture) {
      console.log('Opening conversation:', this.querySelector('.conversation-title').textContent);
    }
  });
}

// Fonction pour attacher les event listeners aux conversations
function attachConversationListeners() {
  const conversationItems = document.querySelectorAll('.conversation-item');
  
  conversationItems.forEach(item => {
    // Supprimer les anciens listeners pour éviter les doublons
    const newItem = item.cloneNode(true);
    item.parentNode.replaceChild(newItem, item);
  });
  
  // Réattacher les nouveaux listeners
  document.querySelectorAll('.conversation-item').forEach(item => {
    attachSwipeListeners(item);
    
    // Ajouter le listener pour la poubelle
    const binIcon = item.querySelector('.bin-icon');
    if (binIcon) {
      binIcon.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const conversationId = parseInt(this.dataset.id);
        const conversationTitle = item.querySelector('.conversation-title').textContent;
        
        if (confirm(`Êtes-vous sûr de vouloir supprimer la conversation "${conversationTitle}" ?`)) {
          // Animation de suppression
          item.style.transition = 'all 0.3s ease-out';
          item.style.transform = 'translateX(-100%)';
          item.style.opacity = '0';
          
          setTimeout(() => {
            deleteConversation(conversationId);
            refreshConversationsDisplay();
          }, 300);
        }
      });
    }
  });
}

// Fonction pour rafraîchir l'affichage des conversations
function refreshConversationsDisplay(sortType = 'date') {
  const conversations = loadConversations();
  const sortedConversations = sortConversations(conversations, sortType);
  const conversationsSection = document.querySelector('.conversations-section');
  
  // Garder le header
  const header = conversationsSection.querySelector('.conversations-header');
  
  // Vider le contenu actuel (sauf le header)
  const existingItems = conversationsSection.querySelectorAll('.conversation-item');
  existingItems.forEach(item => item.remove());
  
  // Ajouter les conversations triées
  sortedConversations.forEach(conversation => {
    const conversationHTML = generateConversationHTML(conversation);
    conversationsSection.insertAdjacentHTML('beforeend', conversationHTML);
  });
  
  // Réattacher les event listeners
  attachConversationListeners();
}

// Export des fonctions pour les utiliser
window.ConversationUtils = {
  formatRelativeDate,
  sortConversations,
  createConversation,
  saveConversations,
  loadConversations,
  deleteConversation,
  generateConversationHTML,
  refreshConversationsDisplay,
  attachConversationListeners,
  attachSwipeListeners
};

// Script principal pour la page des conversations
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing conversations');
    initializeDefaultConversations();    
    refreshConversationsDisplay();
    initializeSearch();
    
    // Ajouter le listener pour le bouton "Nouvelle"
    const addBtn = document.getElementById('addConversationBtn');
    if (addBtn) {
        addBtn.addEventListener('click', function() {
            const title = prompt('Titre de la nouvelle conversation :');
            if (title && title.trim()) {
                createNewConversation(title.trim());
            }
        });
    }
    
    // Mettre à jour les dates toutes les heures
    setInterval(updateRelativeDates, 3600000);
    
    console.log('Conversations initialized successfully');
});

// Fonction pour initialiser les conversations par défaut
function initializeDefaultConversations() {
    let conversations = loadConversations();
    
    // Si aucune conversation n'existe, créer des exemples
    if (conversations.length === 0) {
        const defaultConversations = [
            {
                id: 1,
                title: "Titre 1",
                date: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
                avatarColor: "#f97316",
                avatar: "🐻",
                bin: '🗑️'
            },
            {
                id: 2,
                title: "Titre 2", 
                date: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
                avatarColor: "#ef4444",
                avatar: "🐻",
                bin: '🗑️'
            },
            {
                id: 3,
                title: "Titre 3",
                date: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
                avatarColor: "#10b981",
                avatar: "🐻",
                bin: '🗑️'
            }
        ];
        
        saveConversations(defaultConversations);
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
            const newRelativeDate = formatRelativeDate(isoDate);
            dateElement.textContent = newRelativeDate;
        }
    });
}

// Fonction pour créer une nouvelle conversation (appelée depuis le bouton)
function createNewConversation(title) {
    const colors = ['#60AC9A'];
    const avatars = ['🐻', '🦊', '🐱', '🐶', '🐺', '🦁'];
    const randomColor = colors[Math.floor(Math.random() * colors.length)];
    const randomAvatar = avatars[Math.floor(Math.random() * avatars.length)];
    
    const conversations = loadConversations();
    const newConversation = {
        id: Date.now(),
        title: title,
        date: new Date().toISOString(),
        avatarColor: randomColor,
        avatar: randomAvatar,
        bin: '🗑️'
    };
    
    conversations.push(newConversation);
    saveConversations(conversations);
    refreshConversationsDisplay();
    
    // Faire défiler vers le haut pour voir la nouvelle conversation
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Exposer les fonctions globalement pour le menu React
window.ConversationPageUtils = {
    createNewConversation,
    updateRelativeDates
};