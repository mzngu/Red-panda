from rest_framework.permissions import BasePermission

class IsOwnerOrAdmin(BasePermission):
    """
    Permission personnalisée qui permet l'accès uniquement au propriétaire de l'objet
    ou aux utilisateurs avec statut admin (staff).
    """

    def has_object_permission(self, request, view, obj):
        # L'accès est autorisé si l'utilisateur est admin
        if request.user and request.user.is_staff:
            return True
        # Ou si l'utilisateur est le propriétaire de l'objet
        return obj.utilisateur == request.user  # ou obj.owner, selon ton modèle