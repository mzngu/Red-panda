from rest_framework import serializers
from .models import Utilisateur, Ordonnance, Medicament, Allergie, AntecedentMedical

class UtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = [
            'id', 'email', 'nom', 'prenom', 'password', 'date_naissance',
            'nationalite', 'adresse', 'code_postal', 'numero_telephone', 'role'
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'style': {'input_type': 'password'}}
        }

    def create(self, validated_data):
        """Crée un nouvel utilisateur avec un mot de passe haché."""
        return Utilisateur.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Met à jour un utilisateur et gère le hachage du mot de passe si nécessaire."""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

class MedicamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicament
        # On exclut 'ordonnance' car il est géré par le contexte (l'OrdonnanceSerializer)
        fields = ['id', 'nom', 'description', 'dose', 'composant']

class OrdonnanceSerializer(serializers.ModelSerializer):
    utilisateur = serializers.ReadOnlyField(source='utilisateur.email')
    # Le serializer de médicament est maintenant utilisé pour la création et la lecture imbriquées
    medicaments = MedicamentSerializer(many=True)
    class Meta:
        model = Ordonnance
        fields = '__all__'

    def create(self, validated_data):
        """Gère la création de l'ordonnance et de ses médicaments associés."""
        medicaments_data = validated_data.pop('medicaments')
        ordonnance = Ordonnance.objects.create(**validated_data)
        for medicament_data in medicaments_data:
            Medicament.objects.create(ordonnance=ordonnance, **medicament_data)
        return ordonnance

    def update(self, instance, validated_data):
        """Gère la mise à jour de l'ordonnance et de ses médicaments associés."""
        medicaments_data = validated_data.pop('medicaments', None)

        # Met à jour les champs de l'ordonnance (nom, date, etc.)
        instance = super().update(instance, validated_data)

        if medicaments_data is not None:
            # Pour la mise à jour, la stratégie la plus simple est de supprimer
            # les anciens médicaments et de créer les nouveaux.
            instance.medicaments.all().delete()
            for medicament_data in medicaments_data:
                Medicament.objects.create(ordonnance=instance, **medicament_data)
        return instance

class AllergieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Allergie
        fields = '__all__'

class AntecedentMedicalSerializer(serializers.ModelSerializer):
    class Meta:
        model = AntecedentMedical
        fields = '__all__'