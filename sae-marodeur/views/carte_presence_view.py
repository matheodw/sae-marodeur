"""Vue PyQt pour l'affichage de la carte de présence.
Contient les widgets nécessaires pour visualiser les données en direct.
"""
from PyQt6.QtWidgets import QWidget
class CartePresenceView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Carte des enseignants - Style Maraudeur")

