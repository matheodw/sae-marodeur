from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QVBoxLayout, QLabel, QApplication
from PyQt5.QtCore import pyqtSignal, Qt

class LoginView(QWidget):
    """
    User connection interface.
    This view provides input fields for username and password.It communicates with the LoginController via signals.
    """

    login_signal = pyqtSignal(str, str)
    
    def __init__(self):
        """
        Initializes the LoginView window.
        Sets window properties and triggers UI building.
        """
        super().__init__()
        self.setWindowTitle("Maraudeur - Connexion")
        self.setMinimumSize(400, 450)
        self.init_ui()
    
    def init_ui(self):
        """
        Initializes and styles the graphical user interface components.
        
        Sets up the title, input fields with placeholder text, 
        and the login button with QSS styling.
        """
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # --- LOGO / TITLE ---
        title = QLabel("MARAUDEUR")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)

        subtitle = QLabel("Identifiez-vous pour continuer")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #7f8c8d; font-size: 14px; margin-bottom: 20px;")
        layout.addWidget(subtitle)
        
        # --- INPUT FIELDS STYLE ---
        input_style = """
            QLineEdit {
                padding: 12px;
                border: 1px solid #dcdde1;
                border-radius: 5px;
                background-color: #f5f6fa;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
                background-color: #ffffff;
            }
        """

        self.username = QLineEdit()
        self.username.setPlaceholderText("Utilisateur")
        self.username.setStyleSheet(input_style)
        layout.addWidget(self.username)
        
        self.password = QLineEdit()
        self.password.setPlaceholderText("Mot de passe")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setStyleSheet(input_style)
        self.password.returnPressed.connect(self.emit_login)
        layout.addWidget(self.password)
        
        # --- CONNECTION BUTTON ---
        btn_login = QPushButton("Connecter")
        btn_login.setCursor(Qt.PointingHandCursor)
        btn_login.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c5980;
            }
        """)
        btn_login.clicked.connect(self.emit_login)
        layout.addWidget(btn_login)
        
        layout.addStretch()
        
        # --- FOOTER ---
        footer = QLabel("SAE - Développé des applications communicantes - 2026")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #bdc3c7; font-size: 10px;")
        layout.addWidget(footer)

    def emit_login(self):
        """
        Retrieves the input texts and emits the login signal to the controller.
        The username is stripped of leading/trailing whitespace before emission.
        """
        user = self.username.text().strip()
        pwd = self.password.text()
        self.login_signal.emit(user, pwd)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    view = LoginView()
    view.show()
    sys.exit(app.exec_())