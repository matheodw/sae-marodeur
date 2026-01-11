"""
Authentication logic management module.
Contains the controller that bridges the login view and the database.
"""

import os
import sys
from PyQt5.QtCore import pyqtSignal, QObject

class LoginController(QObject):
    """
    Controller managing user authentication logic.

    This class connects the graphical interface (LoginView) to the data model (User)
    and validates credentials via the database.

    :ivar authentication_success: Signal emitted on successful login, carries a User object.
    :vartype authentication_success: pyqtSignal(object)
    :ivar authentication_failed: Signal emitted on failure, carries an error message.
    :vartype authentication_failed: pyqtSignal(str)
    """

    # Signal emitting a User OBJECT (important for HomeView)
    authentication_success = pyqtSignal(object)  
    authentication_failed = pyqtSignal(str)
    
    def __init__(self):
        """
        Initializes the controller, configures system paths, and prepares the database.
        """
        super().__init__()
        
        # Path configuration
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if base_dir not in sys.path:
            sys.path.insert(0, base_dir)
            
        from views.login_view import LoginView
        from models.user import User
        from server.database import Database 
        
        self.view = LoginView()
        self.view.login_signal.connect(self.authenticate)
        self.User = User
        
        # Database connection (Clean path)
        db_path = os.path.join(base_dir, "marodeur.db")
        self.db = Database(db_path)
        
        self._setup_test_users()

    def _setup_test_users(self):
        """
        Creates test users in the database if they do not exist.
        
        This private method is called at startup to ensure the presence of
        admin, secretary, cleaner, and director profiles.
        """
        users_to_create = [
            {"username": "admin", "password": "admin", "role": "administration", "nom": "Admin", "prenom": "System"},
            {"username": "secretary", "password": "secretary123", "role": "secretary", "nom": "Jacqautl", "prenom": "Jennifer"},
            {"username": "cleaner", "password": "cleaner123", "role": "cleaner", "nom": "Durant", "prenom": "Marie"},
            {"username": "director", "password": "director123", "role": "director of studies", "nom": "Durand", "prenom": "Jean"}
        ]
        for u in users_to_create:
            self.db.create_user(u['username'], u['password'], u['role'], u['nom'], u['prenom'])

    def authenticate(self, username, password):
        """
        Verifies provided credentials and instantiates a User object for the session.

        :param username: The entered username.
        :type username: str
        :param password: The entered password.
        :type password: str
        
        :raises Exception: If a database connection error occurs.
        :return: Emits authentication_success(user) if valid, otherwise authentication_failed(msg).
        :rtype: None
        """
        if not username or not password:
            self.authentication_failed.emit("Please fill in all fields")
            return
        
        try:
            user_data = self.db.authenticate_user(username, password)
            
            if user_data:
                # Creating User object from the dictionary received from the DB
                user = self.User(
                    id=user_data.get("id"),
                    username=user_data.get("username"),
                    role=user_data.get("role"),
                    nom=user_data.get("nom"),
                    prenom=user_data.get("prenom"),
                    created_at=user_data.get("created_at")
                )
                
                print(f"Connected: {user.prenom} {user.nom}")
                
                # Emit the full User object
                self.authentication_success.emit(user)
            else:
                self.authentication_failed.emit("Invalid credentials")
                
        except Exception as e:
            print(f"Authentication error: {e}")
            self.authentication_failed.emit("Connection error")
    
    def show(self):
        """
        Displays the login user interface.
        """
        self.view.show()