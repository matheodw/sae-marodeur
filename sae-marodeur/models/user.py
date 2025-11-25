"""Modèle représentant un utilisateur.
Gère les attributs : identifiant, rôle, permissions, etc.
"""
class User:
    def __init__(self, username, role):
        self.username = username
        self.role = role