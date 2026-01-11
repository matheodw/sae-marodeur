import sqlite3
from datetime import datetime
from typing import List, Optional

class Salle:
    """
    Model representing a room (Salle) and its availability status.

    This class manages room metadata and provides methods to query the database 
    to determine if a room is currently occupied based on recorded presences.

    :param id: Unique database identifier for the room.
    :type id: int
    :param numero: Room number or name (e.g., 'A101').
    :type numero: str
    :param batiment: Building name or identifier.
    :type batiment: str
    :param etage: Floor number.
    :type etage: int
    :param capacite: Maximum seating capacity.
    :type capacite: int
    :param type_salle: Category of the room (e.g., 'Amphi', 'TD').
    :type type_salle: str
    :param occupee: Current occupancy status, defaults to False.
    :type occupee: bool
    """

    def __init__(self, id, numero, batiment, etage, capacite, type_salle, occupee=False):
        """Initializes a Salle instance with its physical and status attributes."""
        self.id = id
        self.numero = numero
        self.batiment = batiment
        self.etage = etage
        self.capacite = capacite
        self.type_salle = type_salle
        self.occupee = occupee

    def __repr__(self):
        """Returns a string representation: Salle(numero=..., occupee=...)."""
        return f"Salle(numero={self.numero}, occupee={self.occupee})"

    # ----------------------------
    # INTERNAL METHODS
    # ----------------------------

    @staticmethod
    def _connect():
        """
        Establishes a connection to the 'marodeur.db' SQLite database.
        
        :return: sqlite3 connection with Row factory.
        """
        conn = sqlite3.connect("marodeur.db")
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _is_occupee(salle_id: int) -> bool:
        """
        Checks the database to see if a specific room is currently occupied.

        A room is considered occupied if there is an entry in the 'presences' table 
        where the current time falls between 'date_debut' and 'date_fin'.

        :param salle_id: The ID of the room to check.
        :return: True if occupied, False otherwise.
        """
        now = datetime.now()
        with Salle._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) AS count
                FROM presences
                WHERE salle_id = ?
                AND date_debut <= ?
                AND (date_fin IS NULL OR date_fin >= ?)
            """, (salle_id, now, now))
            return cursor.fetchone()["count"] > 0

    @staticmethod
    def _from_row(row) -> "Salle":
        """
        Maps a database row to a Salle object and calculates its occupancy.

        :param row: sqlite3.Row containing room data.
        :return: An initialized Salle instance.
        """
        salle = Salle(
            id=row["id"],
            numero=row["numero"],
            batiment=row["batiment"],
            etage=row["etage"],
            capacite=row["capacite"],
            type_salle=row["type_salle"]
        )
        salle.occupee = Salle._is_occupee(salle.id)
        return salle

    # ----------------------------
    # PUBLIC METHODS
    # ----------------------------

    @classmethod
    def get_by_numero(cls, numero: str) -> Optional["Salle"]:
        """
        Fetches a specific room by its number.

        :param numero: The room number to search for.
        :return: A Salle instance or None if not found.
        """
        with cls._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM salles WHERE numero = ?", (numero,))
            row = cursor.fetchone()
            return cls._from_row(row) if row else None

    @classmethod
    def get_all(cls) -> List["Salle"]:
        """
        Retrieves all rooms from the database, ordered by room number.

        :return: A list of all Salle objects.
        """
        with cls._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM salles ORDER BY numero")
            return [cls._from_row(row) for row in cursor.fetchall()]

    @classmethod
    def get_libres(cls) -> List["Salle"]:
        """
        Filters the database to return only available (not occupied) rooms.

        :return: A list of available Salle objects.
        """
        return [s for s in cls.get_all() if not s.occupee]

    @classmethod
    def get_occupees(cls) -> List["Salle"]:
        """
        Filters the database to return only occupied rooms.

        :return: A list of occupied Salle objects.
        """
        return [s for s in cls.get_all() if s.occupee]
