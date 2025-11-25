"""Modèle représentant une salle.
Comprend les attributs liés à la disponibilité et aux propriétés de la salle.
"""
class Salle:
    def __init__(self, numero, occupee=False):
        self.numero = numero
        self.occupee = occupee