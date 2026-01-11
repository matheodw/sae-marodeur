"""Gestionnaire de plusieurs personnes.
Permet de gérer une collection de personnes.

Auteur: Équipe projet
Date de création: 2024
Dernière modification: 2024
"""

from .personne import Personne


class Personnes:
    """
    Gère une collection de personnes.
    
    Args:
        personnes: Liste de Personne (optionnel, par défaut liste vide)
    
    Exemple:
        >>> personnes = Personnes()
        >>> p1 = Personne("Dupont", "I4-101", "etudiant")
        >>> personnes.ajouter(p1)
        >>> print(len(personnes.liste))
        1
    """
    def __init__(self, personnes=None):
        """
        Initialise le gestionnaire de personnes.
        
        Args:
            personnes: Liste initiale de Personne (optionnel)
        """
        self.liste = personnes if personnes is not None else []
    
    def ajouter(self, personne):
        """
        Ajoute une personne à la liste.
        
        Args:
            personne: Instance de Personne à ajouter
        """
        if isinstance(personne, Personne):
            self.liste.append(personne)
    
    def get_by_salle(self, salle):
        """
        Récupère toutes les personnes dans une salle donnée.
        
        Args:
            salle: Numéro de la salle
            
        Returns:
            Liste des Personne dans cette salle
        """
        return [p for p in self.liste if p.salle == salle]
    
    def get_by_type(self, type_personne):
        """
        Récupère toutes les personnes d'un type donné.
        
        Args:
            type_personne: Type de personne ("etudiant" ou "enseignant")
            
        Returns:
            Liste des Personne de ce type
        """
        return [p for p in self.liste if p.type_personne == type_personne]
    
    def __len__(self):
        """Retourne le nombre de personnes."""
        return len(self.liste)
    
    def __repr__(self):
        """Représentation textuelle du gestionnaire."""
        return f"Personnes({len(self.liste)} personnes)"

