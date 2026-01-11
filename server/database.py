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
        """Initialise la base de données."""
        self.db_path = db_path
        # On initialise les tables au démarrage
        self._init_database()
        print(f"DB initialisée sur : {self.db_path}")

    def get_connection(self):
        """Crée une nouvelle connexion ponctuelle (évite le verrouillage)."""
        conn = sqlite3.connect(self.db_path, timeout=30)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
        except:
            pass
        return conn
    
    def _init_database(self):
        """Initialise les tables de la base de données si elles n'existent pas."""
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
        """Hash un mot de passe avec SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def close(self):
        """Inutile maintenant car on ferme à chaque appel, mais gardé pour compatibilité."""
        pass
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
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
        presences = self.get_presences()
        map_data = {}
        for p in presences:
            salle = p["salle"]
            if salle not in map_data:
                map_data[salle] = []
            map_data[salle].append({"nom": p["nom_complet"], "type": p["type_personne"]})
        return {"presences": presences, "by_salle": map_data, "timestamp": datetime.now().isoformat()}
    
    def get_salles_libres(self) -> List[Dict[str, Any]]:
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
        """Supprime les présences antérieures à une date donnée."""
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