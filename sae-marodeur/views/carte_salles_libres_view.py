"""Vue affichant les salles libres sous forme de tableau ou liste.
Le contrôleur met à jour son contenu selon les données du serveur.
"""
from PyQt6.QtWidgets import QWidget
class CarteSallesLibresView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Salles libres")