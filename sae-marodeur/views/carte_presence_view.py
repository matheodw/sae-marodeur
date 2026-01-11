
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableWidget, QTableWidgetItem, QLabel, QHeaderView
)
from PyQt5.QtCore import pyqtSignal, Qt

class CartePresenceView(QWidget):
    """
    View for the attendance map featuring a role-filtered sidebar.
    This view displays student names, their current room locations, and 
    their attendance status in a structured table.
    """
    
    go_to_presence_signal = pyqtSignal()
    go_to_salles_libres_signal = pyqtSignal()
    go_to_recherche_etudiant_signal = pyqtSignal()
    go_to_administration_signal = pyqtSignal()
    retour_signal = pyqtSignal()
    
    def __init__(self, profile=None):
        """
        Initializes the attendance map view.
        :param profile: Dictionary containing user session information (e.g., role).
        :type profile: dict, optional
        """
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        self.profile = profile or {}
        self.role = str(self.profile.get('role', '')).lower().strip()
        
        self.setWindowTitle("Maraudeur - Carte des présences")
        self.setMinimumSize(1000, 600)
        self.init_ui()
    
    def _has_permission(self, feature):
        """
        Verifies access rights based on the user's role.
        :param feature: The key of the feature to check access for.
        :type feature: str
        :return: True if the role has access to the feature, False otherwise.
        :rtype: bool
        """
        permissions = {
            'presence': ['secretaire', 'directeur_etudes', 'directeur des etudes', 'administration'],
            'salles_libres': ['femme_menage', 'femme de menage', 'directeur_etudes', 'directeur des etudes', 'administration', 'secretaire'],
            'recherche': ['secretaire', 'directeur_etudes', 'directeur des etudes', 'administration'],
            'admin': ['administration']
        }
        return self.role in permissions.get(feature, [])

    def get_sidebar_style(self, active=False):
        """
        Returns the style for sidebar buttons.
        :param active: Whether the button is currently selected/active.
        :type active: bool
        :return: A formatted QSS string for QPushButton.
        :rtype: str
        """
        bg = "#e0e0e0" if active else "transparent"
        weight = "bold" if active else "normal"
        return (f"QPushButton {{ background-color: {bg}; border: none; padding: 15px; "
                f"text-align: left; font-weight: {weight}; border-radius: 5px; }} "
                f"QPushButton:hover {{ background-color: #e8e8e8; }}")

    def init_ui(self):
        """
        Initializes the graphical user interface.
        """
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # --- Sidebar ---
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("background-color: #f5f5f5; border-right: 1px solid #ddd;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        
        nav_items = [
            ("Carte des présences", self.go_to_presence_signal, 'presence'),
            ("Salles libres", self.go_to_salles_libres_signal, 'salles_libres'),
            ("Recherche étudiant", self.go_to_recherche_etudiant_signal, 'recherche'),
            ("Administration", self.go_to_administration_signal, 'admin')
        ]
        
        for text, sig, perm in nav_items:
            if self._has_permission(perm):
                btn = QPushButton(text)
                btn.setStyleSheet(self.get_sidebar_style(perm == 'presence'))
                btn.clicked.connect(sig.emit)
                sidebar_layout.addWidget(btn)
        
        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar)

        # --- Main Content ---
        content = QWidget()
        content.setStyleSheet("background-color: white;")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("Carte des présences")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333; margin-bottom: 10px;")
        layout.addWidget(title)
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Nom", "Salle", "Statuts"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)
        
        btn_retour = QPushButton("Retour au menu")
        btn_retour.setFixedWidth(150)
        btn_retour.setCursor(Qt.PointingHandCursor)
        btn_retour.setStyleSheet("padding: 8px; background-color: #f0f0f0; border-radius: 4px;")
        btn_retour.clicked.connect(self.retour_signal.emit)
        layout.addWidget(btn_retour, alignment=Qt.AlignRight)
        
        main_layout.addWidget(content)

    def load_presences(self, presences):
        """
        Fills the table with attendance data provided by the controller.
        :param presences: List of dictionaries containing attendance records.
        :type presences: list
        """
        self.table.setRowCount(0)
        for p in (presences or []):
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(p.get('nom', 'Unknown'))))
            self.table.setItem(row, 1, QTableWidgetItem(str(p.get('salle', 'N/A'))))
            self.table.setItem(row, 2, QTableWidgetItem(str(p.get('statut', 'Present'))))

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    sys.exit(app.exec_())