"""Modèle représentant une personne (étudiant ou personnel).
Contient les informations générales liées à une personne.

Auteur: Équipe projet
Date de création: 2024
Dernière modification: 2024
"""


class Personne:
    """
    Représente une personne (étudiant ou enseignant).
    
    Args:
        nom: Nom de la personne
        salle: Numéro de la salle où se trouve la personne (peut être None)
        type_personne: Type de personne ("etudiant" ou "enseignant", optionnel)
    
    Exemple:
        >>> p = Personne("Dupont", "I4-101", "etudiant")
        >>> print(p.nom)
        Dupont
    """
    def __init__(self, nom, salle=None, type_personne=None):
        """
        Initialise une personne.
        
        Args:
            nom: Nom de la personne
            salle: Numéro de la salle (optionnel)
            type_personne: Type de personne (optionnel)
        """
        self.nom = nom
        self.salle = salle
        self.type_personne = type_personne
    
    def __repr__(self):
        """Représentation textuelle de la personne."""
        return f"Personne(nom={self.nom}, salle={self.salle}, type={self.type_personne})"