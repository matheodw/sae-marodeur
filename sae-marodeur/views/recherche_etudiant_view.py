from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableWidget, QTableWidgetItem, QLabel, QHeaderView, QLineEdit
)
from PyQt5.QtCore import pyqtSignal, Qt

class RechercheEtudiantView(QWidget):
    """
    Search view with navigation filtering based on user roles.
    This view allows authorized users to search for students and see their 
    current location or status within the establishment.
    """
    
    go_to_presence_signal = pyqtSignal()
    go_to_salles_libres_signal = pyqtSignal()
    go_to_recherche_etudiant_signal = pyqtSignal()
    go_to_administration_signal = pyqtSignal()
    retour_signal = pyqtSignal()
    
    search_signal = pyqtSignal(str)
    
    def __init__(self, profile=None):
        """
        Initializes the student search view.
        :param profile: Dictionary containing user session information (role, etc.).
        :type profile: dict, optional
        """
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        self.profile = profile or {}
        self.role = str(self.profile.get('role', '')).lower().strip()
        
        self.setWindowTitle("Maraudeur - Recherche Étudiant")
        self.setMinimumSize(1000, 600)
        self.init_ui()
    
    def _has_permission(self, feature):
        """
        Verifies access rights based on the standardized user role.
        :param feature: The key of the feature to check access for.
        :type feature: str
        :return: True if access is granted, False otherwise.
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
        Returns the sidebar button style harmonized with other views.
        :param active: Whether the button represents the current active page.
        :type active: bool
        :return: A formatted QSS string for the button style.
        :rtype: str
        """
        bg = "#e0e0e0" if active else "transparent"
        weight = "bold" if active else "normal"
        return (f"QPushButton {{ background-color: {bg}; border: none; padding: 15px; "
                f"text-align: left; font-weight: {weight}; border-radius: 5px; }} "
                f"QPushButton:hover {{ background-color: #e8e8e8; }}")

    def init_ui(self):
        """
        Initializes the graphical user interface, sidebar, and search table.
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
                btn.setStyleSheet(self.get_sidebar_style(perm == 'recherche')) # Actif
                btn.clicked.connect(sig.emit)
                sidebar_layout.addWidget(btn)
        
        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar)

        # --- Main content ---
        content = QWidget()
        content.setStyleSheet("background-color: white;")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("Recherche d'étudiant")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # search box
        search_box = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Entrez le nom de l'étudiant...")
        self.search_input.setStyleSheet("padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 14px;")
        self.search_input.returnPressed.connect(self.do_search)
        
        btn_search = QPushButton("Rechercher")
        btn_search.setCursor(Qt.PointingHandCursor)
        btn_search.setStyleSheet("""
            QPushButton { background-color: #3498db; color: white; padding: 12px 20px; 
            border-radius: 5px; font-weight: bold; }
            QPushButton:hover { background-color: #2980b9; }
        """)
        btn_search.clicked.connect(self.do_search)
        
        search_box.addWidget(self.search_input)
        search_box.addWidget(btn_search)
        layout.addLayout(search_box)
        
        # Table of results
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Nom de l'étudiant", "Salle actuelle / Statut"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)
        
        # Footer
        footer_layout = QHBoxLayout()
        btn_retour = QPushButton("Retour au Menu")
        btn_retour.setFixedWidth(150)
        btn_retour.setStyleSheet("padding: 8px; background-color: #f0f0f0; border-radius: 4px;")
        btn_retour.clicked.connect(self.retour_signal.emit)
        
        footer_layout.addStretch()
        footer_layout.addWidget(btn_retour)
        layout.addLayout(footer_layout)
        
        main_layout.addWidget(content)
    
    def do_search(self):
        """
        Retrieves the search query from the input field and emits the search signal.
        """
        query = self.search_input.text().strip()
        if query:
            self.search_signal.emit(query)
    
    def load_results(self, results):
        """
        Populates the table with search results provided by the controller.
        :param results: List of dictionaries containing student location data.
        :type results: list
        """
        self.table.setRowCount(0)
        for res in (results or []):
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(res.get('nom', 'Inconnu'))))
            self.table.setItem(row, 1, QTableWidgetItem(str(res.get('salle', 'N/A'))))

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    sys.exit(app.exec_())