import { defineMiddleware } from 'astro:middleware';

// Le middleware s'exécute pour chaque requête
export const onRequest = defineMiddleware(async (context, next) => {
  // Exemple : Protéger toutes les routes API
  if (context.url.pathname.startsWith('/api/')) {
    // Ici, vous vérifieriez un cookie de session ou un token d'authentification
    const isLoggedIn = context.cookies.has('session_id');

    if (!isLoggedIn) {
      // Si l'utilisateur n'est pas connecté, on renvoie une erreur 401 (Non autorisé)
      return new Response(JSON.stringify({ message: 'Accès non autorisé' }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' },
      });
    }
  }

  // Si tout va bien, on passe à la requête suivante (votre page ou API)
  return next();
});