import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

class NavigationManager:
    """
    Manages application navigation and access rights between different views.
    This class follows the MVC (Model-View-Controller) architecture to handle
    switching between controllers while maintaining user session data.
    """
    
    PERMISSIONS = {
        'presence': ['secretaire', 'directeur_etudes', 'directeur des etudes', 'administration'],
        'salles_libres': ['femme_menage', 'femme de menage', 'directeur_etudes', 'directeur des etudes', 'administration', 'secretaire'],
        'recherche': ['secretaire', 'directeur_etudes', 'directeur des etudes', 'administration'],
        'admin': ['administration']
    }

    def __init__(self):
        """
        Initializes the NavigationManager and the QApplication instance.
        """
        self.app = QApplication(sys.argv)
        self.current_controller = None
        self.user_profile = None
        
    def start(self):
        """
        Starts the application by displaying the login page and entering the main event loop.
        """
        self.show_login()
        sys.exit(self.app.exec_())

    def check_access(self, feature):
        """
        Verifies if the currently logged-in user has the required role for a feature.
        :param feature: The name of the feature to check access for.
        :type feature: str
        :return: True if access is granted, False otherwise.
        """
        if not self.user_profile:
            return False
        role = str(self.user_profile.get('role', '')).lower().strip()
        return role in self.PERMISSIONS.get(feature, [])

    def _clear_current_view(self):
        """
        Safely hides the current view and releases resources.
        """
        if self.current_controller:
            if hasattr(self.current_controller, 'close_connection'):
                self.current_controller.close_connection()
            
            if hasattr(self.current_controller, 'view') and self.current_controller.view:
                self.current_controller.view.hide()
                self.current_controller.view.deleteLater()
            
            self.current_controller = None

    def _connect_sidebar(self, view):
        """
        Connects common navigation signals found in sidebars across different views.
        :param view: The view instance containing the signals.
        """
        if not view: 
            return
        
        signals = {
            'retour_signal': self.show_home,
            'go_to_presence_signal': self.show_presence,
            'go_to_salles_libres_signal': self.show_salles_libres,
            'go_to_recherche_etudiant_signal': self.show_recherche_etudiant,
            'go_to_administration_signal': self.show_administration
        }

        for sig_name, method in signals.items():
            sig = hasattr(view, sig_name) and getattr(view, sig_name)
            if sig:
                try: 
                    sig.disconnect()
                except: 
                    pass
                sig.connect(method)

    # --- NAVIGATION METHODS ---

    def show_login(self):
        """
        Displays the Login view and connects authentication success/failure signals.
        """
        self._clear_current_view()
        from controllers.login_controller import LoginController
        self.current_controller = LoginController()
        self.current_controller.authentication_success.connect(self.on_login_success)
        self.current_controller.authentication_failed.connect(self.on_login_failed)
        self.current_controller.show()
    
    def on_login_success(self, user):
        """
        Handles successful authentication by creating a session profile and redirecting to home.

        :param user: The user object returned by the login controller.
        :type user: User
        """
        self.user_profile = {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "nom": user.nom,
            "prenom": user.prenom
        }
        print(f"Session opened: {user.username} ({user.role})")
        self.show_home()
    
    def on_login_failed(self, error):
        """
        Displays an error message upon failed authentication.

        :param error: The error message to display.
        :type error: str
        """
        QMessageBox.warning(None, "Authentication Failed", error)

    def _navigate_to(self, controller_class, feature_name=None):
        """
        Generic method to handle transitions between controllers with permission checks.
        :param controller_class: The class of the controller to instantiate.
        :type controller_class: class
        """
        if feature_name and not self.check_access(feature_name):
            QMessageBox.critical(None, "Access Denied", "You do not have sufficient rights.")
            return

        self._clear_current_view()
        self.current_controller = controller_class(self.user_profile)
        self._connect_sidebar(self.current_controller.view)
        self.current_controller.show()

    def show_home(self):
        """
        Navigates to the Home dashboard.
        """
        from controllers.home_controller import HomeController
        self._navigate_to(HomeController)
    
    def show_presence(self):
        """
        Navigates to the Presence Map view.
        """
        from controllers.carte_presence_controller import CartePresenceController
        self._navigate_to(CartePresenceController, 'presence')
    
    def show_salles_libres(self):
        """
        Navigates to the Free Rooms view.
        """
        from controllers.salles_libres_controller import SallesLibresController
        self._navigate_to(SallesLibresController, 'salles_libres')
    
    def show_recherche_etudiant(self):
        """
        Navigates to the Student Search view.
        """
        from controllers.recherche_etudiant_controller import RechercheEtudiantController
        self._navigate_to(RechercheEtudiantController, 'recherche')
    
    def show_administration(self):
        """
        Navigates to the Administration panel.
        """
        from controllers.admin_controller import AdminController
        self._navigate_to(AdminController, 'admin')

if __name__ == "__main__":
    NavigationManager().start()