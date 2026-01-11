import sys
import os
import random
from PyQt5.QtWidgets import QMessageBox

# --- PATH CONFIGURATION ---
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from views.admin_comptes_view import AdminComptesView

try:
    from server.database import Database
except ImportError:
    from server.database import Database

class AdminController:
    """
    Controller responsible for administrative tasks related to user accounts.
    This class handles the creation and deletion by communicating directly with the SQLite database.
    """

    def __init__(self, user_profile=None):
        """
        Initializes the AdminController.
        :param user_profile: Dictionary containing the current admin's session info.
        :type user_profile: dict, optional
        """
        self.user_profile = user_profile
        base_projet = os.path.dirname(ROOT_DIR)
        self.db_path = os.path.normpath(os.path.join(base_projet, "marodeur.db"))
        self.db = Database(db_path=self.db_path)
        self.view = AdminComptesView(profile=self.user_profile)
        self.connect_signals()
        self.refresh_user_list()

    def connect_signals(self):
        """
        Establishes connections between the view's interactive elements and controller methods.
        """
        try:
            self.view.add_account_signal.disconnect()
            self.view.delete_account_signal.disconnect()
        except:
            pass
            
        self.view.add_account_signal.connect(self.handle_add_account)
        self.view.delete_account_signal.connect(self.handle_delete_account)

    def refresh_user_list(self):
        """
        Retrieves the latest user list from the database and updates the view.
        """
        try:
            users = self.db.get_all_users()
            
            if users is not None:
                self.view.load_users(users)
            else:
                print("DEBUG: La base de données a renvoyé 'None' pour les utilisateurs.")
        except Exception as e:
            print(f"DEBUG: Erreur lors de la lecture DB : {e}")

    def handle_add_account(self):
        """
        Creates a new user account with a randomized username for testing purposes.
        """
        username = f"agent_{random.randint(100, 999)}"
        
        try:
            success = self.db.create_user(
                username=username,
                password="123",
                role="secretaire",
                nom="Agent",
                prenom="Nouveau"
            )
            
            if success:
                print(f"Succès: {username} créé.")
                self.refresh_user_list()
            else:
                QMessageBox.warning(self.view, "Erreur", "L'ajout a échoué.")
                
        except Exception as e:
            print(f"Erreur lors de l'ajout : {e}")

    def handle_delete_account(self, user_id):
        """
        Deletes a specific user account after confirmation.
        :param user_id: The unique identifier of the user to delete.
        :type user_id: str or int
        """
        if not user_id:
            return

        confirm = QMessageBox.question(
            self.view, "Confirmation",
            f"Supression de l'ID de l'agent N°{user_id}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            try:
                if self.db.delete_user(int(user_id)):
                    print(f"Agent {user_id} supprimé.")
                    self.refresh_user_list()
                else:
                    QMessageBox.warning(self.view, "Erreur", "Suppression impossible.")
            except Exception as e:
                print(f"Erreur lors de la suppression : {e}")

    def show(self):
        """
        Displays the admin management window.
        """
        if self.view:
            self.view.show()

    def close_connection(self):
        """
        Properly closes the database connection and cleans up resources.
        """
        if hasattr(self, 'db'):
            try:
                self.db.close()
            except:
                pass
            del self.db 
            print("Connexion Database fermée.")