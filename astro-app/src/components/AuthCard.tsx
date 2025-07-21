import React, { useState } from 'react';
import { Card, CardContent } from "./ui/card";

type AuthCardProps = {
  mode: "login" | "signup";
  onSubmit?: (e: React.FormEvent<HTMLFormElement>) => void;
};

const AuthCard: React.FC<AuthCardProps> = ({ mode, onSubmit }) => {
  const isLogin = mode === "login";
  const [formData, setFormData] = useState({
    email: '',
    mot_de_passe: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Validation côté client
      if (!formData.email || !formData.mot_de_passe) {
        setError('Veuillez remplir tous les champs');
        setLoading(false);
        return;
      }

      if (!isLogin) {
        // Validation pour l'inscription
        if (formData.mot_de_passe !== formData.confirmPassword) {
          setError('Les mots de passe ne correspondent pas');
          setLoading(false);
          return;
        }
      }

      const endpoint = isLogin ? '/auth/login' : '/auth/register';
      const payload = isLogin 
        ? {
            email: formData.email,
            mot_de_passe: formData.mot_de_passe
          }
        : {
            email: formData.email,
            mot_de_passe: formData.mot_de_passe,
            role: 'utilisateur'
          };

      console.log('Envoi des données:', payload);

      const response = await fetch(`http://localhost:8080${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(payload)
      });

      console.log('Response status:', response.status);
      
      let data;
      try {
        data = await response.json();
        console.log('Response data:', data);
      } catch (jsonError) {
        console.error('Erreur parsing JSON:', jsonError);
        throw new Error('Réponse serveur invalide');
      }

      if (!response.ok) {
        // Gestion spécifique des erreurs
        if (response.status === 422) {
          throw new Error('Données invalides. Vérifiez vos informations.');
        } else if (response.status === 400) {
          throw new Error(data.detail || 'Données incorrectes');
        } else if (response.status === 401) {
          throw new Error('Email ou mot de passe incorrect');
        } else if (response.status === 405) {
          throw new Error('Erreur de configuration du serveur');
        } else {
          throw new Error(data.detail || `Erreur ${response.status}`);
        }
      }

      // Succès - rediriger vers la page d'accueil
      console.log('Succès:', data.message);
      window.location.href = '/home/home';
      
    } catch (err) {
      console.error('Erreur complète:', err);
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Une erreur inattendue est survenue');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto">
      {/* Zone pour la mascotte */}
      <div className="flex justify-center mb-8">
        <div className="w-32 h-32 rounded-full bg-gradient-to-br from-teal-300 to-teal-500 flex items-center justify-center shadow-lg">
          <div className="w-24 h-24 rounded-full bg-gradient-to-br from-teal-200 to-teal-400 flex items-center justify-center">
            <img 
              src="/sorrel/pandSayingHi.png" 
              alt="Mascotte Don't Panic" 
              className="w-20 h-20 object-contain"
              onError={(e) => {
                e.currentTarget.style.display = 'none';
                e.currentTarget.nextElementSibling?.classList.remove('hidden');
              }}
            />
            <div className="text-4xl hidden">🦊</div>
          </div>
        </div>
      </div>

      <Card className="w-full rounded-3xl shadow-xl bg-white">
        <CardContent className="p-8 space-y-6">
          {/* Header avec flèche et titre */}
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-black">
              DON'T PANIC
            </h2>
            <div className="text-xl font-bold text-black">→</div>
          </div>

          {/* Affichage des erreurs */}
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <form className="space-y-6" onSubmit={handleSubmit}>
            <div>
              <label className="text-sm font-medium text-black block mb-2">
                Adresse mail :
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                className="w-full border-b-2 border-cyan-400 outline-none pb-2 bg-transparent text-black placeholder-gray-500"
                placeholder=""
              />
            </div>

            <div>
              <label className="text-sm font-medium text-black block mb-2">
                Mot de passe :
              </label>
              <input
                type="password"
                name="mot_de_passe"
                value={formData.mot_de_passe}
                onChange={handleChange}
                required
                className="w-full border-b-2 border-cyan-400 outline-none pb-2 bg-transparent text-black placeholder-gray-500"
                placeholder=""
              />
            </div>

            {!isLogin && (
              <div>
                <label className="text-sm font-medium text-black block mb-2">
                  Confirmer le mot de passe :
                </label>
                <input
                  type="password"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  required
                  className="w-full border-b-2 border-cyan-400 outline-none pb-2 bg-transparent text-black placeholder-gray-500"
                  placeholder=""
                />
              </div>
            )}

            {/* Mot de passe oublié (seulement pour login) */}
            {isLogin && (
              <div className="text-right">
                <a 
                  href="/mot-de-passe-oublie/mot-de-passe-oublie" 
                  className="text-sm text-cyan-500 hover:text-cyan-600 transition-colors"
                >
                  Mot de passe oublié?
                </a>
              </div>
            )}

            {/* Bouton principal */}
            <div className="pt-4">
              <button
                type="submit"
                disabled={loading}
                className="w-full py-4 text-lg font-bold bg-gray-100 hover:bg-gray-200 text-black border-2 border-gray-300 rounded-full transition-all duration-200 disabled:opacity-50"
              >
                {loading ? "Chargement..." : (isLogin ? "SE CONNECTER" : "S'INSCRIRE")}
              </button>
            </div>

            {/* Lien vers l'autre mode */}
            <div className="text-center pt-4">
              {isLogin ? (
                <a 
                  href="/inscription/inscription" 
                  className="text-sm text-red-500 hover:text-red-600 transition-colors"
                >
                  Je n'ai pas de compte
                </a>
              ) : (
                <a 
                  href="/connexion/connexion" 
                  className="text-sm text-red-500 hover:text-red-600 transition-colors"
                >
                  J'ai déjà un compte
                </a>
              )}
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default AuthCard;