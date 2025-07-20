import React from 'react';
import { Card, CardContent } from "./ui/card";

type AuthCardProps = {
  mode: "login" | "signup";
  onSubmit?: (e: React.FormEvent<HTMLFormElement>) => void;
};

const AuthCard: React.FC<AuthCardProps> = ({ mode, onSubmit = () => {} }) => {
  const isLogin = mode === "login";

  return (
    <div className="w-full max-w-md mx-auto">
      {/* Zone pour la mascotte */}
      <div className="flex justify-center mb-8">
        <div className="w-32 h-32 rounded-full bg-gradient-to-br from-teal-300 to-teal-500 flex items-center justify-center shadow-lg">
          <div className="w-24 h-24 rounded-full bg-gradient-to-br from-teal-200 to-teal-400 flex items-center justify-center">
            {/* Image de la mascotte avec fallback */}
            <img 
              src="/sorrel/pandSayingHi.png" 
              alt="Mascotte Don't Panic" 
              className="w-20 h-20 object-contain"
              onError={(e) => {
                // Fallback si l'image n'existe pas
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

          <form className="space-y-6" onSubmit={onSubmit}>
            <div>
              <label className="text-sm font-medium text-black block mb-2">
                Adresse mail :
              </label>
              <input
                type="email"
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
                className="w-full py-4 text-lg font-bold bg-gray-100 hover:bg-gray-200 text-black border-2 border-gray-300 rounded-full transition-all duration-200"
              >
                {isLogin ? "SE CONNECTER" : "S'INSCRIRE"}
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