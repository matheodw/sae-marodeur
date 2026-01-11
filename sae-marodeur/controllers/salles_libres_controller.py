"""
Controller for the Free Rooms feature.
Handles the logic between the database and the SallesLibresView.
"""

from views.carte_salles_libres_view import CarteSallesLibresView

class SallesLibresController:
    """
    Manages the logic for free rooms.
    """

    def __init__(self, user_profile=None):
        """
        Initializes the controller and its associated view.

        :param user_profile: Dictionary containing user session data.
        """
        self.user_profile = user_profile
        # Initialize the view
        self.view = CarteSallesLibresView(profile=self.user_profile)
        
        # We no longer call self.load_data() here to keep it clean

    def show(self):
        """
        Displays the associated view.
        """
        self.view.show()

    def update_view(self, rooms_list):
        """
        Public method to update the view with a real list of rooms.
        Can be called from the NavigationManager or a database trigger.

        :param rooms_list: List of dictionaries (e.g., [{'nom': 'B102'}, ...])
        """
        self.view.load_rooms(rooms_list)

    def close_connection(self):
        """
        Safely closes any resources before the controller is destroyed.
        """
        # Add database closing logic here if necessary
        pass