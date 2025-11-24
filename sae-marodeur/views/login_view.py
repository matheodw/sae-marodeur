# login_view.py
from PyQt6.QtWidgets import QWidget, QPushButton, QLineEdit, QVBoxLayout
from PyQt6.QtCore import pyqtSignal


class LoginView(QWidget):
    login_signal = pyqtSignal(str, str)


    def __init__(self):
        super().__init__()
        self.setWindowTitle("Connexion")


        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        btn = QPushButton("Connexion")


        layout = QVBoxLayout()
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(btn)
        self.setLayout(layout)


        btn.clicked.connect(self.emit_login)


    def emit_login(self):
        self.login_signal.emit(self.username.text(), self.password.text())