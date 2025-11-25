"""Contrôleur responsable de la gestion de la carte de présence.
Récupère les données des modèles et met à jour la vue correspondante.
"""
class CartePresenceController:
    def __init__(self):
        from nomprojet.views.carte_presence_view import CartePresenceView
        self.view = CartePresenceView()


    def load_data(self):
        pass


    def show(self):
        self.view.show()