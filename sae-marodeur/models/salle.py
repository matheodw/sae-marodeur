"""Modèle représentant une salle.
Comprend les attributs liés à la disponibilité et aux propriétés de la salle.

Auteur: Équipe projet
Date de création: 2024
Dernière modification: 2024
"""


class Salle:
    """
    Représente une salle du département.
    
    Args:
        numero: Numéro de la salle (ex: "I4-101")
        occupee: True si la salle est occupée, False sinon (par défaut False)
        capacite: Capacité de la salle en nombre de places (optionnel)
    
    Exemple:
        >>> s = Salle("I4-101", occupee=True, capacite=30)
        >>> print(s.numero)
        I4-101
    """
    def __init__(self, numero, occupee=False, capacite=None):
        """
        Initialise une salle.
        
        Args:
            numero: Numéro de la salle
            occupee: État d'occupation (par défaut False)
            capacite: Capacité de la salle (optionnel)
        """
        self.numero = numero
        self.occupee = occupee
        self.capacite = capacite
    
    def __repr__(self):
        """Représentation textuelle de la salle."""
        return f"Salle(numero={self.numero}, occupee={self.occupee}, capacite={self.capacite})"