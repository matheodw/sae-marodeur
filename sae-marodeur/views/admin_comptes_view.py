"""
User Account Management View for the SAE Marodeur application.
Provides an interface for administrators to view, add, and delete user accounts.
"""
import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableWidget, QTableWidgetItem, QLabel, QHeaderView, QApplication
)
from PyQt5.QtCore import pyqtSignal, Qt

class AdminComptesView(QWidget):
    """
    Refined view for user account administration.
    
    This view features a dynamic sidebar based on user roles and a central
    management table with action triggers.
    """
    
    # Navigation Signals
    go_to_presence_signal = pyqtSignal()
    go_to_salles_libres_signal = pyqtSignal()
    go_to_recherche_etudiant_signal = pyqtSignal()
    go_to_administration_signal = pyqtSignal()
    retour_signal = pyqtSignal()
    
    # Action Signals
    add_account_signal = pyqtSignal()
    delete_account_signal = pyqtSignal(str) 
    
    def __init__(self, profile=None):
        """
        Initializes the administration view.

        :param profile: Dictionary containing user session information (e.g., role).
        :type profile: dict, optional
        """
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        self.profile = profile or {}
        # Normalize role string
        self.role = str(self.profile.get('role', '')).lower().strip()
        
        self.setWindowTitle("Administration - User Accounts")
        self.setMinimumSize(1000, 600)
        self.init_ui()
    
    def _has_permission(self, feature):
        """
        Internal check to verify access rights based on the user's role.

        :param feature: The key of the feature to check.
        :type feature: str
        :return: True if the role is authorized, False otherwise.
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
        Generates the QSS style string for sidebar buttons.

        :param active: Whether the button represents the current active page.
        :type active: bool
        :return: A formatted CSS string for the QPushButton.
        """
        bg = "#e0e0e0" if active else "transparent"
        weight = "bold" if active else "normal"
        return (f"QPushButton {{ background-color: {bg}; border: none; padding: 15px; "
                f"text-align: left; font-weight: {weight}; border-radius: 5px; }} "
                f"QPushButton:hover {{ background-color: #e8e8e8; }}")

    def init_ui(self):
        """
        Sets up the main layout, sidebar, and content area.
        """
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # --- Sidebar ---
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("background-color: #f5f5f5; border-right: 1px solid #ddd;")
        sidebar_layout = QVBoxLayout(sidebar)
        
        nav_items = [
            ("Présences", self.go_to_presence_signal, 'presence'),
            ("Salles libres", self.go_to_salles_libres_signal, 'salles_libres'),
            ("Recherche", self.go_to_recherche_etudiant_signal, 'recherche'),
            ("Administration", self.go_to_administration_signal, 'admin')
        ]
        
        for text, sig, perm in nav_items:
            if self._has_permission(perm):
                btn = QPushButton(text)
                btn.setStyleSheet(self.get_sidebar_style(perm == 'admin'))
                btn.clicked.connect(sig.emit)
                sidebar_layout.addWidget(btn)
        
        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar)

        content = QWidget()
        content.setStyleSheet("background-color: white;")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header Section
        header = QHBoxLayout()
        title = QLabel("Administration des comptes utilisateurs")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header.addWidget(title)
        
        btn_add = QPushButton("+ Ajouter un compte")
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.setStyleSheet("""
            QPushButton { background-color: #4CAF50; color: white; padding: 8px 15px; 
            border-radius: 4px; font-weight: bold; } 
            QPushButton:hover { background-color: #45a049; }
        """)
        btn_add.clicked.connect(self.add_account_signal.emit)
        header.addWidget(btn_add)
        layout.addLayout(header)
        
        # Accounts Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Nom d'utilisateur", "Role", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        
        # Footer Navigation
        btn_retour = QPushButton("Retour au Menu")
        btn_retour.setFixedWidth(150)
        btn_retour.setStyleSheet("padding: 8px; background-color: #f0f0f0; border-radius: 4px;")
        btn_retour.clicked.connect(self.retour_signal.emit)
        layout.addWidget(btn_retour, alignment=Qt.AlignRight)
        
        main_layout.addWidget(content)

    def load_users(self, users):
        """
        Populates the table with user data.

        :param users: List of dictionaries containing user details (id, username, role).
        :type users: list
        """
        self.table.setRowCount(0)
        for u in (users or []):
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            uid = str(u.get("id", ""))
            
            item_id = QTableWidgetItem(uid)
            item_id.setTextAlignment(Qt.AlignCenter)
            
            self.table.setItem(row, 0, item_id)
            self.table.setItem(row, 1, QTableWidgetItem(u.get("username", "")))
            self.table.setItem(row, 2, QTableWidgetItem(u.get("role", "")))
            
            btn_del = QPushButton("Supprimer")
            btn_del.setStyleSheet("""
                QPushButton { background-color: #ff4d4d; color: white; border-radius: 3px; padding: 4px; } 
                QPushButton:hover { background-color: #ff3333; }
            """)
            btn_del.setProperty("user_id", uid)
            btn_del.clicked.connect(self._handle_delete_click)
            self.table.setCellWidget(row, 3, btn_del)

    def _handle_delete_click(self):
        """
        Internal handler that extracts the User ID from the sender button properties 
        and emits the deletion signal.
        """
        btn = self.sender()
        if btn and btn.property("user_id"):
            self.delete_account_signal.emit(btn.property("user_id"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    view = AdminComptesView(profile={"role": "administration"})
    view.load_users([{"id": 1, "username": "admin", "role": "administration"}])
    view.show()
    sys.exit(app.exec_())