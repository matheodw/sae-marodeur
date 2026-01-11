from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QApplication
from PyQt5.QtCore import pyqtSignal, Qt

class HomeView(QWidget):
    """
    This view serves as the landing page after authentication. It dynamically
    generates navigation buttons based on the permissions associated with 
    the user's role.
    """
    
    go_to_presence_signal = pyqtSignal()
    go_to_salles_libres_signal = pyqtSignal()
    go_to_recherche_etudiant_signal = pyqtSignal()
    go_to_administration_signal = pyqtSignal()
    
    def __init__(self, profile):
        """
        Initializes the HomeView with user profile data.
        :param profile: User profile data. Can be a User object or a dictionary.
        :type profile: Union[User, dict]
        """
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.profile = profile
        if hasattr(profile, 'username'):
            self.username = profile.username
            self.role = str(profile.role).lower().strip()
        else:
            self.username = profile.get('username', 'User')
            self.role = str(profile.get('role', '')).lower().strip()
        
        self.setWindowTitle("Maraudeur - Menu principal")
        self.setMinimumSize(500, 500)
        self.init_ui()
    
    def _has_permission(self, feature):
        """
        Verifies if the current user has access to a specific feature.
        :param feature: The key of the feature to check (e.g., 'presence', 'admin').
        :type feature: str
        :return: True if the user role is authorized, False otherwise.
        :rtype: bool
        """
        permissions = {
            'presence': ['secretaire', 'directeur_etudes', 'directeur des etudes', 'administration'],
            'salles_libres': ['femme_menage', 'femme de menage', 'directeur_etudes', 'directeur des etudes', 'administration', 'secretaire'],
            'recherche': ['secretaire', 'directeur_etudes', 'directeur des etudes', 'administration'],
            'admin': ['administration']
        }
        return self.role in permissions.get(feature, [])

    def init_ui(self):
        """
        Initializes the user interface and builds the dynamic menu.
        """
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(60, 50, 60, 50)
        
        # --- Header ---
        welcome_label = QLabel(f"Bienvenue, {self.username}")
        welcome_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        welcome_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome_label)

        role_label = QLabel(f"Session: {self.role.capitalize()}")
        role_label.setStyleSheet("font-size: 13px; color: #95a5a6; margin-bottom: 20px;")
        role_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(role_label)

        # --- Menu Button Style ---
        btn_style = """
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #dcdde1;
                border-radius: 8px;
                padding: 15px;
                font-size: 15px;
                color: #2f3640;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #f5f6fa;
                border-color: #3498db;
                color: #3498db;
            }
        """

        menu_items = [
            ("Carte des présences", self.go_to_presence_signal, 'presence'),
            ("Salles libres", self.go_to_salles_libres_signal, 'salles_libres'),
            ("Recherche etudiants", self.go_to_recherche_etudiant_signal, 'recherche'),
            ("Administration", self.go_to_administration_signal, 'admin')
        ]

        for text, sig, perm in menu_items:
            if self._has_permission(perm):
                btn = QPushButton(text)
                btn.setCursor(Qt.PointingHandCursor)
                btn.setStyleSheet(btn_style)
                btn.clicked.connect(sig.emit)
                layout.addWidget(btn)

        layout.addStretch()
        
        # Footer
        footer = QLabel("Maraudeur v1.0")
        footer.setStyleSheet("color: #bdc3c7; font-size: 10px;")
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    sys.exit(app.exec_())