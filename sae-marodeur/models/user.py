"""Modèle User représentant un utilisateur.
Récupère toutes les informations depuis la base de données du serveur.
"""
import os
import sqlite3
from typing import Optional


class User:
    """Modèle utilisateur qui récupère les données depuis la base de données."""
    
    def __init__(self, id: int = None, username: str = None, role: str = None,
                 nom: str = None, prenom: str = None, created_at: str = None,
                 password: str = None, salle: str = None):
        
        self.id = id
        self.username = username
        
        # --- NORMALISATION DU RÔLE ---
        # Si la BDD renvoie "administration", on peut avoir besoin de "Administration"
        # On stocke la valeur brute
        self.role = role
        
        # On assure la compatibilité avec les anciens noms
        self.nom = nom if nom else username
        self.prenom = prenom
        self.created_at = created_at
        self.password = password
        self.salle = salle
        
        # Attribut pour compatibilité avec tes anciens contrôleurs
        self.type_personne = role
        
        # DEBUG : Ajoute cette ligne temporairement pour voir ce qui arrive de la BDD
        # print(f"DEBUG LOGIN: User={self.username}, Role={self.role}")

    def verify_password(self, password_to_check: str) -> bool:
        """
        Vérifie si le mot de passe correspond.
        
        :param password_to_check: Mot de passe à vérifier
        :return: True si le mot de passe correspond, False sinon
        """
        return self.password == password_to_check

    @classmethod
    def _get_db_path(cls) -> str:
        """
        Retourne le chemin vers la base de données du serveur.
        Calculé selon l'arborescence du projet.
        """
        # Ton calcul de chemin d'origine
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        db_path = os.path.join(base_dir, "marodeur.db")
        
        # Sécurité : si le fichier n'est pas trouvé au chemin complexe, 
        # on cherche dans le dossier courant
        if not os.path.exists(db_path):
            return "marodeur.db"
            
        return db_path
    
    @classmethod
    def get_by_username(cls, username: str) -> Optional['User']:
        """
        Récupère un utilisateur par son nom d'utilisateur.
        """
        db_path = cls._get_db_path()
        
        try:
            # "with" ferme la connexion automatiquement après le bloc
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, username, role, nom, prenom, created_at, password
                    FROM users
                    WHERE username = ?
                """, (username,))
                
                row = cursor.fetchone()
                
                if row:
                    return cls(
                        id=row["id"],
                        username=row["username"],
                        role=row["role"],
                        nom=row["nom"],
                        prenom=row["prenom"],
                        created_at=row["created_at"],
                        password=row["password"]
                    )
                return None
        except Exception as e:
            print(f"Erreur User.get_by_username: {e}")
            return None
    
    @classmethod
    def get_by_id(cls, user_id: int) -> Optional['User']:
        """
        Récupère un utilisateur par son ID.
        """
        db_path = cls._get_db_path()
        
        try:
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, username, role, nom, prenom, created_at, password
                    FROM users
                    WHERE id = ?
                """, (user_id,))
                
                row = cursor.fetchone()
                
                if row:
                    return cls(
                        id=row["id"],
                        username=row["username"],
                        role=row["role"],
                        nom=row["nom"],
                        prenom=row["prenom"],
                        created_at=row["created_at"],
                        password=row["password"]
                    )
                return None
        except Exception as e:
            print(f"Erreur User.get_by_id: {e}")
            return None
    
    @classmethod
    def get_all(cls) -> list['User']:
        """
        Récupère tous les utilisateurs depuis la base de données.
        """
        db_path = cls._get_db_path()
        
        try:
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, username, role, nom, prenom, created_at, password
                    FROM users
                    ORDER BY username
                """)
                
                users = []
                for row in cursor.fetchall():
                    users.append(cls(
                        id=row["id"],
                        username=row["username"],
                        role=row["role"],
                        nom=row["nom"],
                        prenom=row["prenom"],
                        created_at=row["created_at"],
                        password=row["password"]
                    ))
                
                return users
        except Exception as e:
            print(f"Erreur User.get_all: {e}")
            return []