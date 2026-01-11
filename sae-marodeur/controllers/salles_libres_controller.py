from models.salle import Salle
from views.carte_salles_libres_view import CarteSallesLibresView


class SallesLibresController:
    """
    Controller responsible for managing and displaying available (free) rooms.

    This class interacts with the ``Salle`` model to filter for unoccupied rooms
    and updates the ``CarteSallesLibresView`` to present this information to the user.

    :param user_profile: Profile of the current user, defaults to None.
    :type user_profile: object, optional
    """

    def __init__(self, user_profile=None):
        """
        Initializes the controller, sets up the view, and triggers data loading.
        """
        self.user_profile = user_profile
        self.view = CarteSallesLibresView(profile=user_profile)
        self.load_data()

    def load_data(self):
        """
        Retrieves the list of available rooms from the Model and populates the View.

        The process follows these steps:
            1. Calls the static method ``Salle.get_libres()`` to get room objects.
            2. Iterates through the results to extract the room number.
            3. Formats the data into a list of dictionaries with 'nom' and 'statut' keys.
            4. Passes the formatted list to ``self.view.load_rooms()``.
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
        Renders and displays the Available Rooms view.
        """
        self.view.show()
