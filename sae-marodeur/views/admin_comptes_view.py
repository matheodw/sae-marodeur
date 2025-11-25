"""Vue PyQt affichant l'interface de gestion des comptes.
Définit les éléments graphiques et signaux liés aux actions admin.
"""
from PyQt6.QtWidgets import QWidget
class AdminComptesView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestion des utilisateurs")