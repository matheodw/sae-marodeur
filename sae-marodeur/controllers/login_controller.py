"""Gère la logique d'authentification utilisateur."""
import os
import sys
from PyQt5.QtCore import pyqtSignal, QObject

class LoginController(QObject):
    """Contrôleur gérant l'authentification avec le modèle User."""
    
    # On garde l'émission d'un OBJET User (important pour ta HomeView)
    authentication_success = pyqtSignal(object)  
    authentication_failed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        # Configuration des chemins
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if base_dir not in sys.path:
            sys.path.insert(0, base_dir)
            
        from views.login_view import LoginView
        from models.user import User  # ON GARDE LE MODELE ICI
        from server.database import Database 
        
        self.view = LoginView()
        self.view.login_signal.connect(self.authenticate)
        self.User = User
        
        # Connexion à la DB (Chemin propre)
        db_path = os.path.join(base_dir, "marodeur.db")
        self.db = Database(db_path)
        
        self._setup_test_users()

    def _setup_test_users(self):
        """Crée les utilisateurs de test."""
        users_to_create = [
            {"username": "admin", "password": "admin", "role": "administration", "nom": "Admin", "prenom": "Système"},
            {"username": "secretaire", "password": "secretaire123", "role": "secretaire", "nom": "Jacqautl", "prenom": "Jennifer"},
            {"username": "menage", "password": "menage123", "role": "femme de menage", "nom": "Durant", "prenom": "Marie"},
            {"username": "directeur", "password": "directeur123", "role": "directeur des etudes", "nom": "Durand", "prenom": "Jean"}
        ]
        for u in users_to_create:
            self.db.create_user(u['username'], u['password'], u['role'], u['nom'], u['prenom'])

    def authenticate(self, username, password):
        """Vérifie les identifiants et crée un objet User pour la session."""
        if not username or not password:
            self.authentication_failed.emit("Veuillez remplir tous les champs")
            return
        
        try:
            user_data = self.db.authenticate_user(username, password)
            
            if user_data:
                # Création de l'objet User à partir du dictionnaire reçu de la DB
                # On utilise les clés du dictionnaire user_data
                user = self.User(
                    id=user_data.get("id"),
                    username=user_data.get("username"),
                    role=user_data.get("role"),
                    nom=user_data.get("nom"),
                    prenom=user_data.get("prenom"),
                    created_at=user_data.get("created_at")
                )
                
                print(f"Connecté : {user.prenom} {user.nom}")
                
                # On envoie l'objet User complet
                self.authentication_success.emit(user)
            else:
                self.authentication_failed.emit("Identifiants incorrects")
                
        except Exception as e:
            print(f"Erreur d'authentification : {e}")
            self.authentication_failed.emit("Erreur de connexion")
    
    def show(self):
        self.view.show()