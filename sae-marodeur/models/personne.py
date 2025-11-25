"""Modèle représentant une personne (étudiant ou personnel).
Contient les informations générales liées à une personne.
"""
class Personne:
    def __init__(self, nom, salle):
        self.nom = nom
        self.salle = salle