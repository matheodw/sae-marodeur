"""
Model representing a person (student or staff).
Contains general information related to an individual within the system.

Author: Project Team
Creation Date: 2024
Last Modified: 2024
"""

class Personne:
    """
    Represents a person (typically a student or a teacher).

    This class serves as a basic data model to store and manage the identity
    and current location of individuals.

    :param nom: The full name of the person.
    :type nom: str
    :param salle: The room number where the person is located, defaults to None.
    :type salle: str, optional
    :param type_personne: The category of the person (e.g., "etudiant" or "enseignant"), defaults to None.
    :type type_personne: str, optional

    **Example:**

    >>> p = Personne("Dupont", "I4-101", "etudiant")
    >>> print(p.nom)
    Dupont
    """

    def __init__(self, nom, salle=None, type_personne=None):
        """
        Initializes a new Person instance.

        :param nom: Name of the person.
        :param salle: Room number (optional).
        :param type_personne: Person type/category (optional).
        """
        self.nom = nom
        self.salle = salle
        self.type_personne = type_personne

    def __repr__(self):
        """
        Returns a developer-friendly string representation of the Person object.
        
        :return: A string containing the name, room, and type of the person.
        :rtype: str
        """
        return f"Personne(nom={self.nom}, salle={self.salle}, type={self.type_personne})"
