"""Gère la connexion et les interactions avec la base de données.
Contient les requêtes SQL utilisées par le serveur.
"""
import sqlite3
import hashlib
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

class Database:
    """Classe gérant toutes les interactions avec la base de données."""
    
    def __init__(self, db_path: str = "marodeur.db"):
        """
        Initialize the database and create tables if missing.

        :param db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self._init_database()
        print(f"DB initialisée sur : {self.db_path}")

    def get_connection(self):
        """
        Create and return a new SQLite connection.

        The returned connection uses WAL and sqlite3.Row for rows.

        :return: sqlite3.Connection
        """
        conn = sqlite3.connect(self.db_path, timeout=30)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
        except:
            pass
        return conn
    
    def _init_database(self):
        """
        Create required tables and ensure a default admin user exists.

        :return: None
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Table des utilisateurs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    nom TEXT,
                    prenom TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table des salles
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS salles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero TEXT UNIQUE NOT NULL,
                    batiment TEXT,
                    etage TEXT,
                    capacite INTEGER,
                    type_salle TEXT
                )
            """)
            
            # Table des personnes (enseignants/étudiants)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS personnes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT NOT NULL,
                    prenom TEXT NOT NULL,
                    type TEXT NOT NULL,
                    code_up_planning TEXT,
                    email TEXT
                )
            """)
            
            # Table des présences
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS presences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    personne_id INTEGER NOT NULL,
                    salle_id INTEGER NOT NULL,
                    date_debut TIMESTAMP NOT NULL,
                    date_fin TIMESTAMP,
                    FOREIGN KEY (personne_id) REFERENCES personnes(id),
                    FOREIGN KEY (salle_id) REFERENCES salles(id)
                )
            """)
            
            # Table des plannings
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS plannings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    personne_id INTEGER,
                    salle_id INTEGER,
                    code_up_planning TEXT,
                    date_debut TIMESTAMP,
                    date_fin TIMESTAMP,
                    description TEXT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (personne_id) REFERENCES personnes(id),
                    FOREIGN KEY (salle_id) REFERENCES salles(id)
                )
            """)
            
            conn.commit()
            
            # Créer un utilisateur admin par défaut si vide
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                self._create_default_admin(conn)
        finally:
            cursor.close()
            conn.close()
    
    def _create_default_admin(self, conn):
        """
        Insert a default admin user if none exists.

        :param conn: sqlite3.Connection to use for insertion.
        """
        default_password = "admin"
        password_hash = self._hash_password(default_password)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO users (username, password_hash, role, nom, prenom)
                VALUES (?, ?, ?, ?, ?)
            """, ("admin", password_hash, "administration", "Admin", "Système"))
            conn.commit()
            print("Utilisateur admin créé (username: admin, password: admin)")
        finally:
            cursor.close()
    
    def _hash_password(self, password: str) -> str:
        """
        Hashes a plain-text password using SHA-256.
        
        :param password: The raw password string.
        :return: A 64-character hexadecimal hash.
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def close(self):
        """
        No-op. Connections are created per-method; included for API compatibility.

        :return: None
        """
        pass
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user.

        :param username: Username string.
        :param password: Plain-text password.
        :return: Dict with user fields on success, otherwise None.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            password_hash = self._hash_password(password)
            cursor.execute("""
                SELECT id, username, role, nom, prenom
                FROM users
                WHERE username = ? AND password_hash = ?
            """, (username, password_hash))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        finally:
            cursor.close()
            conn.close()
      
    def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Return a list of all users.

        :return: List of user dicts.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id, username, role, nom, prenom, created_at
                FROM users
                ORDER BY username
            """)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()
    
    def create_user(self, username: str, password: str, role: str,
                   nom: Optional[str] = None, prenom: Optional[str] = None) -> Optional[int]:
        """
        Create a new user.

        :param username: Username.
        :param password: Plain-text password.
        :param role: User role.
        :param nom: Optional last name.
        :param prenom: Optional first name.
        :return: New user id on success, None on failure.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            password_hash = self._hash_password(password)
            cursor.execute("""
                INSERT INTO users (username, password_hash, role, nom, prenom)
                VALUES (?, ?, ?, ?, ?)
            """, (username, password_hash, role, nom, prenom))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
        except Exception as e:
            print(f"Erreur create_user: {e}")
            conn.rollback()
            return None
        finally:
            cursor.close()
            conn.close()
    
    def update_user(self, user_id: int, data: Dict[str, Any]) -> bool:
        """
        Update a user's fields.

        :param user_id: ID of the user to update.
        :param data: Field values to update (supports 'password' to change password).
        :return: True if a row was updated, False otherwise.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            updates = []
            values = []
            for key, val in data.items():
                if key == "password":
                    updates.append("password_hash = ?")
                    values.append(self._hash_password(val))
                else:
                    updates.append(f"{key} = ?")
                    values.append(val)
            
            if not updates:
                return False
            
            values.append(user_id)
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Erreur update_user: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
    
    def delete_user(self, user_id: int) -> bool:
        """
        Delete a user by id.

        :param user_id: ID of the user to delete.
        :return: True if deletion occurred, False otherwise.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"ERREUR DB lors de la suppression: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
    
    def get_presences(self) -> List[Dict[str, Any]]:
        """
        Return current presences active at now.

        :return: List of presence dicts.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        now = datetime.now()
        try:
            cursor.execute("""
                SELECT p.id, p.nom || ' ' || p.prenom AS nom_complet, s.numero AS salle,
                       pres.date_debut, pres.date_fin, p.type AS type_personne
                FROM presences pres
                JOIN personnes p ON pres.personne_id = p.id
                JOIN salles s ON pres.salle_id = s.id
                WHERE pres.date_debut <= ? AND (pres.date_fin IS NULL OR pres.date_fin >= ?)
                ORDER BY s.numero, p.nom
            """, (now, now))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()
    
    def get_presence_map(self) -> Dict[str, Any]:
        """
        Return presences grouped by room with a timestamp.

        :return: Dict with 'presences', 'by_salle' and 'timestamp'.
        """
        presences = self.get_presences()
        map_data = {}
        for p in presences:
            salle = p["salle"]
            if salle not in map_data:
                map_data[salle] = []
            map_data[salle].append({"nom": p["nom_complet"], "type": p["type_personne"]})
        return {"presences": presences, "by_salle": map_data, "timestamp": datetime.now().isoformat()}
    
    def get_salles_libres(self) -> List[Dict[str, Any]]:
        """
        Return rooms that are free right now.

        :return: List of room dicts.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        now = datetime.now()
        try:
            cursor.execute("""
                SELECT * FROM salles 
                WHERE id NOT IN (
                    SELECT DISTINCT salle_id FROM presences 
                    WHERE date_debut <= ? AND (date_fin IS NULL OR date_fin >= ?)
                )
            """, (now, now))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()

    def search_etudiant(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for students by name.

        :param query: Search string to match against name fields.
        :return: List of matching student dicts with current room if any.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        now = datetime.now()
        search_term = f"%{query}%"
        try:
            cursor.execute("""
                SELECT p.id, p.nom || ' ' || p.prenom AS nom_complet, s.numero AS salle
                FROM personnes p
                LEFT JOIN presences pres ON p.id = pres.personne_id
                    AND pres.date_debut <= ? AND (pres.date_fin IS NULL OR pres.date_fin >= ?)
                LEFT JOIN salles s ON pres.salle_id = s.id
                WHERE p.type = 'etudiant'
                AND (p.nom LIKE ? OR p.prenom LIKE ? OR p.nom || ' ' || p.prenom LIKE ?)
            """, (now, now, search_term, search_term, search_term))
            results = []
            for row in cursor.fetchall():
                results.append({"id": row["id"], "nom": row["nom_complet"], "salle": row["salle"] or "Non trouvé"})
            return results
        finally:
            cursor.close()
            conn.close()

    def update_presence_from_planning(self, personne_id: int, salle_id: int,
                                     date_debut: datetime, date_fin: Optional[datetime]):
        """
        Ensure a presence exists for a planning entry; insert if missing.

        :param personne_id: Person ID.
        :param salle_id: Room ID.
        :param date_debut: Start datetime.
        :param date_fin: Optional end datetime.
        :return: None
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id FROM presences
                WHERE personne_id = ? AND salle_id = ? AND date_debut = ?
            """, (personne_id, salle_id, date_debut))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO presences (personne_id, salle_id, date_debut, date_fin)
                    VALUES (?, ?, ?, ?)
                """, (personne_id, salle_id, date_debut, date_fin))
                conn.commit()
        finally:
            cursor.close()
            conn.close()
            
    def clear_old_presences(self, before_date: datetime):
        """
        Delete presences ending before the given date.

        :param before_date: Datetime threshold; presences ending before this are removed.
        :return: None
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                DELETE FROM presences
                WHERE date_fin < ?
            """, (before_date,))
            conn.commit()
        finally:
            cursor.close()
            conn.close()
