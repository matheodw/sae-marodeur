import sqlite3
from typing import Optional, List

class User:
    """
    Model representing an application user and their authentication data.

    This class handles user profiles, role assignments, and provides the 
    interface for database-driven authentication.

    :param id: Unique database identifier for the user, defaults to None.
    :type id: int, optional
    :param username: Unique login name for the user.
    :type username: str, optional
    :param role: User permissions role (e.g., 'admin', 'enseignant').
    :type role: str, optional
    :param nom: Last name of the user.
    :type nom: str, optional
    :param prenom: First name of the user.
    :type prenom: str, optional
    :param created_at: Account creation timestamp.
    :type created_at: str, optional
    :param password: The hashed password stored in the database.
    :type password: str, optional
    """

    def __init__(self, id=None, username=None, role=None,
                 nom=None, prenom=None, created_at=None, password=None):
        """Initializes a User instance and maps roles to person types."""
        self.id = id
        self.username = username
        self.role = role
        self.nom = nom or username
        self.prenom = prenom
        self.created_at = created_at
        self.password = password
        self.type_personne = role

    def verify_password(self, password_to_check: str) -> bool:
        """
        Validates the provided password against the stored hash.

        :param password_to_check: Plain text password provided by the user.
        :return: True if the passwords match, False otherwise.
        :rtype: bool
        """
        return self.password == password_to_check

    # ----------------------------
    # INTERNAL METHODS
    # ----------------------------

    @staticmethod
    def _connect():
        """
        Establishes a connection to the 'marodeur.db' SQLite database.

        :return: A sqlite3.Connection with Row factory.
        """
        conn = sqlite3.connect("marodeur.db")
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _from_row(row) -> "User":
        """
        Factory method to convert a database row into a User object.

        Note:
            Maps the database column 'password_hash' to the object's 'password' attribute.

        :param row: Database row result.
        :return: An initialized User instance.
        """
        return User(
            id=row["id"],
            username=row["username"],
            role=row["role"],
            nom=row["nom"],
            prenom=row["prenom"],
            created_at=row["created_at"],
            password=row["password_hash"]
        )

    # ----------------------------
    # PUBLIC METHODS
    # ----------------------------

    @classmethod
    def get_by_username(cls, username: str) -> Optional["User"]:
        """
        Retrieves a user from the database based on their username.

        :param username: The username to search for.
        :return: A User instance if found, None otherwise.
        """
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
        """
        Retrieves a user from the database based on their unique ID.

        :param user_id: The primary key ID.
        :return: A User instance if found, None otherwise.
        """
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
        """
        Retrieves all registered users from the database, ordered by username.

        :return: A list of all User instances.
        """
        with cls._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users ORDER BY username")
            return [cls._from_row(row) for row in cursor.fetchall()]
