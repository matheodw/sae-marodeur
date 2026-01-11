"""Script pour créer les différents types d'utilisateurs avec leurs droits."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Database


def create_or_update_user(db: Database, username: str, password: str, role: str, 
                          nom: str = None, prenom: str = None):
    """
    Crée un utilisateur s'il n'existe pas, sinon le met à jour.
    """
    user_id = db.create_user(username, password, role, nom, prenom)
    
    # Si l'utilisateur existe déjà, le mettre à jour
    if user_id is None:
        cursor = db.conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if row:
            db.update_user(row[0], {
                "password": password,
                "role": role,
                "nom": nom,
                "prenom": prenom
            })


def create_default_users():
    """
    Crée ou met à jour les utilisateurs par défaut avec leurs rôles respectifs.
    """
    try:
        db = Database("marodeur.db")
        
        users_to_create = [
            {"username": "admin", "password": "admin", "role": "administration", "nom": "Admin", "prenom": "Système"},
            {"username": "secretaire", "password": "secretaire123", "role": "secretaire", "nom": "Jacqautl", "prenom": "Jennifer"},
            {"username": "menage", "password": "menage123", "role": "femme_menage", "nom": "Durant", "prenom": "Marie"},
            {"username": "directeur", "password": "directeur123", "role": "directeur_etudes", "nom": "Durand", "prenom": "Jean"}
        ]
        
        for user_data in users_to_create:
            create_or_update_user(
                db,
                username=user_data["username"],
                password=user_data["password"],
                role=user_data["role"],
                nom=user_data["nom"],
                prenom=user_data["prenom"]
            )
        
        db.close()
        return True
    except Exception as e:
        return False


if __name__ == "__main__":
    result = create_default_users()
    print(result)