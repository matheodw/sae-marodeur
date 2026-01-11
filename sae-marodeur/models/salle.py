import sqlite3
from datetime import datetime
from typing import List, Optional


class Salle:
    def __init__(self, id, numero, batiment, etage, capacite, type_salle, occupee=False):
    

        self.id = id
        self.numero = numero
        self.batiment = batiment
        self.etage = etage
        self.capacite = capacite
        self.type_salle = type_salle
        self.occupee = occupee

    def __repr__(self):
        return f"Salle(numero={self.numero}, occupee={self.occupee})"

    # ----------------------------
    # MÉTHODES INTERNES
    # ----------------------------

    @staticmethod
    def _connect():
        import os
    # On remonte de deux niveaux (depuis models/salle.py vers la racine)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, "marodeur.db")
    
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _is_occupee(salle_id: int) -> bool:
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
    # MÉTHODES PUBLIQUES
    # ----------------------------

    @classmethod
    def get_by_numero(cls, numero: str) -> Optional["Salle"]:
        with cls._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM salles WHERE numero = ?",
                (numero,)
            )
            row = cursor.fetchone()
            return cls._from_row(row) if row else None

    @classmethod
    def get_all(cls) -> List["Salle"]:
        with cls._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM salles ORDER BY numero")
            return [cls._from_row(row) for row in cursor.fetchall()]

    @classmethod
    def get_libres(cls) -> List["Salle"]:
        return [s for s in cls.get_all() if not s.occupee]

    @classmethod
    def get_occupees(cls) -> List["Salle"]:
        return [s for s in cls.get_all() if s.occupee]
