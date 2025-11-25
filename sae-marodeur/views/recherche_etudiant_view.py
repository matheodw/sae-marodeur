"""Vue pour rechercher un étudiant par nom, prénom ou autre critère.
Affiche les résultats sous forme de liste ou tableau.
"""
from PyQt6.QtWidgets import QWidget
class RechercheEtudiantView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Recherche Étudiant")