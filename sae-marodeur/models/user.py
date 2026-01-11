import sqlite3
from typing import Optional, List


class User:
    def __init__(self, id=None, username=None, role=None,
                 nom=None, prenom=None, created_at=None, password=None):
        self.id = id
        self.username = username
        self.role = role
        self.nom = nom or username
        self.prenom = prenom
        self.created_at = created_at
        self.password = password

        self.type_personne = role


    def verify_password(self, password_to_check: str) -> bool:
        return self.password == password_to_check

    # ----------------------------
    # MÉTHODES INTERNES (privées)
    # ----------------------------

    @staticmethod
    def _connect():
        """Connexion simple à la base de données"""
        conn = sqlite3.connect("marodeur.db")
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _from_row(row) -> "User":
        """Transforme une ligne SQL en objet User"""
        return User(
            id=row["id"],
            username=row["username"],
            role=row["role"],
            nom=row["nom"],
            prenom=row["prenom"],
            created_at=row["created_at"],
            password=row["password_hash"]  # La colonne dans la DB s'appelle password_hash
        )

    # ----------------------------
    # MÉTHODES PUBLIQUES
    # ----------------------------

    @classmethod
    def get_by_username(cls, username: str) -> Optional["User"]:
        with cls._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE username = ?",
                (username,)
            )
            row = cursor.fetchone()
            return cls._from_row(row) if row else None

    @classmethod
    def get_by_id(cls, user_id: int) -> Optional["User"]:
        with cls._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            return cls._from_row(row) if row else None

    @classmethod
    def get_all(cls) -> List["User"]:
        with cls._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users ORDER BY username")
            return [cls._from_row(row) for row in cursor.fetchall()]
