from models.salle import Salle
from views.carte_salles_libres_view import CarteSallesLibresView


class SallesLibresController:
    """
    Controller pour la gestion des salles libres.
    """

    def __init__(self, user_profile=None):
        self.user_profile = user_profile
        self.view = CarteSallesLibresView(profile=user_profile)
        self.load_data()

    def load_data(self):
        """
        Récupère les salles libres et les envoie à la vue.
        """
        salles_libres = Salle.get_libres()

        rooms_list = [
            {
                "nom": salle.numero,
                "statut": "Libre"
            }
            for salle in salles_libres
        ]

        self.view.load_rooms(rooms_list)

    def show(self):
        """
        Affiche la vue.
        """
        self.view.show()
