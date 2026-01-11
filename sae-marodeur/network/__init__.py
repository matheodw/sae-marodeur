"""Package réseau pour l'application.
Exporte les utilitaires et classes réseau.
"""
from .client_network import ClientNetwork, ClientNetworkError

__all__ = ["ClientNetwork", "ClientNetworkError"]
