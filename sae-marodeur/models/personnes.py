import sqlite3
from datetime import datetime
from typing import List
from .personne import Personne

class Personnes:
    """
    A collection and data access object (DAO) for Personne instances.

    This class provides static methods to interact with the SQLite database 
    and instance methods to manage in-memory lists of people.

    :param personnes: Initial list of Personne objects, defaults to None.
    :type personnes: List[Personne], optional
    """

    def __init__(self, personnes=None):
        """
        Initializes the Personnes collection.
        """
        self.liste = personnes if personnes is not None else []

    # INTERNAL METHODS

    @staticmethod
    def _connect():
        """
        Establishes a connection to the SQLite database 'marodeur.db'.

        :return: A sqlite3 connection object with Row factory enabled.
        :rtype: sqlite3.Connection
        """
        conn = sqlite3.connect("marodeur.db")
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _from_row(row) -> Personne:
        """
        Factory method to convert a database row into a Personne object.

        Combines 'nom' and 'prenom' columns into a single 'nom_complet' attribute.

        :param row: A dictionary-like row object from the database.
        :return: A Personne instance.
        :rtype: Personne
        """
        nom_complet = f"{row['nom']} {row['prenom']}"
        return Personne(
            nom=nom_complet,
            salle=row["salle"],
            type_personne=row["type"]
        )

    # DATABASE ACCESS

    @classmethod
    def get_personnel(cls) -> List[Personne]:
        """
        Retrieves all teachers currently present based on the current timestamp.

        Performs a SQL JOIN between 'personnes', 'presences', and 'salles' 
        to determine location and availability.

        :return: A list of Personne objects with 'enseignant' type.
        :rtype: List[Personne]
        """
        now = datetime.now()

        with cls._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.nom, p.prenom, p.type, s.numero AS salle
                FROM personnes p
                LEFT JOIN presences pres ON p.id = pres.personne_id
                    AND pres.date_debut <= ?
                    AND (pres.date_fin IS NULL OR pres.date_fin >= ?)
                LEFT JOIN salles s ON pres.salle_id = s.id
                WHERE p.type = 'enseignant'
                ORDER BY p.nom, p.prenom
            """, (now, now))

            return [cls._from_row(row) for row in cursor.fetchall()]

    # LIST MANAGEMENT

    def ajouter(self, personne: Personne):
        """
        Adds a Personne object to the internal list.

        :param personne: The person to add.
        :type personne: Personne
        """
        if isinstance(personne, Personne):
            self.liste.append(personne)

    def get_by_salle(self, salle):
        """
        Filters the internal list by room number.

        :param salle: Room number to search for.
        :return: List of matches.
        :rtype: List[Personne]
        """
        return [p for p in self.liste if p.salle == salle]

    def get_by_type(self, type_personne):
        """
        Filters the internal list by person type.

        :param type_personne: Type to filter (e.g., 'etudiant').
        :return: List of matches.
        :rtype: List[Personne]
        """
        return [p for p in self.liste if p.type_personne == type_personne]

    def __len__(self):
        """Returns the number of people in the list."""
        return len(self.liste)

    def __repr__(self):
        """Returns a string representation of the collection size."""
        return f"Personnes({len(self.liste)} personnes)"
