from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableWidget, QTableWidgetItem, QLabel, QHeaderView, QApplication
)
from PyQt5.QtCore import pyqtSignal, Qt

class CarteSallesLibresView(QWidget):
    """
    View displaying a list of free rooms with role-based sidebar navigation.
    This interface allows staff to quickly locate available spaces within the establishment.
    """
    
    go_to_presence_signal = pyqtSignal()
    go_to_salles_libres_signal = pyqtSignal()
    go_to_recherche_etudiant_signal = pyqtSignal()
    go_to_administration_signal = pyqtSignal()
    retour_signal = pyqtSignal()
    
    def __init__(self, profile=None):
        """
        Initializes the free rooms view.
        :param profile: Dictionary containing user session information (e.g., role).
        :type profile: dict, optional
        """
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        self.profile = profile or {}
        self.role = str(self.profile.get('role', '')).lower().strip()
        
        self.setWindowTitle("Maraudeur - Salle Libres")
        self.setMinimumSize(1000, 600)
        self.init_ui()
    
    def _has_permission(self, feature):
        """
        Verifies access rights based on the standardized user role.
        :param feature: The key of the feature to check.
        :type feature: str
        :return: True if authorized, False otherwise.
        :rtype: bool
        """
        permissions = {
            'presence': ['secretaire', 'directeur_etudes', 'administration'],
            'salles_libres': ['femme_menage', 'directeur_etudes', 'administration', 'secretaire'],
            'recherche': ['secretaire', 'directeur_etudes', 'administration'],
            'admin': ['administration']
        }
        return self.role in permissions.get(feature, [])

    def get_sidebar_style(self, active=False):
        """
        Generates the sidebar button style.
        :param active: True if this is the current page button.
        :type active: bool
        :return: QSS style string.
        :rtype: str
        """
        bg = "#e0e0e0" if active else "transparent"
        weight = "bold" if active else "normal"
        return (f"QPushButton {{ background-color: {bg}; border: none; padding: 15px; "
                f"text-align: left; font-weight: {weight}; border-radius: 5px; }} "
                f"QPushButton:hover {{ background-color: #e8e8e8; }}")

    def init_ui(self):
        """
        Builds the layout including the sidebar and the rooms table.
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
                btn.setStyleSheet(self.get_sidebar_style(perm == 'salles_libres'))
                btn.clicked.connect(sig.emit)
                sidebar_layout.addWidget(btn)
        
        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar)

        # --- Main Content ---
        content = QWidget()
        content.setStyleSheet("background-color: white;")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("Salle Libres")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)
        
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Numéro / Nom", "Statuts"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)
        
        # Footer
        btn_retour = QPushButton("Retrour au menu")
        btn_retour.setFixedWidth(150)
        btn_retour.setStyleSheet("padding: 8px; background-color: #f0f0f0; border-radius: 4px;")
        btn_retour.clicked.connect(self.retour_signal.emit)
        layout.addWidget(btn_retour, alignment=Qt.AlignRight)
        
        main_layout.addWidget(content)

    def load_rooms(self, rooms):
        """
        Updates the table with the list of free rooms.
        :param rooms: List of dictionaries containing room information.
        :type rooms: list
        """
        self.table.setRowCount(0)
        for r in (rooms or []):
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(r.get('nom', 'Unknown Room'))))
            
            status_item = QTableWidgetItem("Available")
            status_item.setForeground(Qt.darkGreen) 
            self.table.setItem(row, 1, status_item)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    sys.exit(app.exec_())