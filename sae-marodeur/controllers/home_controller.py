import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

class HomeController:
    """
    Home page controller.
    Acts as the bridge between the logged-in user (User object) and the menu display.
    It coordinates how the main dashboard is presented based on user credentials.
    """
    
    def __init__(self, user_profile):
        """
        Initializes the home page controller.
        :param user_profile: Instance of models.user.User representing the connected user.
        :type user_profile: User
        """
        from views.home_view import HomeView
        self.user_profile = user_profile
        
        try:
            self.view = HomeView(profile=self.user_profile)
        except Exception as e:
            print(f"Erreur lors de l'initialisation de HomeView : {e}")
            self.view = None

    def show(self):
        """
        Displays the home window.
        Checks if the view was properly initialized before calling the show method.
        """
        if self.view:
            self.view.show()
        else:
            print("Erreur : La vue d'accueil n'a pas pu être chargée.")
    
    def get_user_profile(self):
        """
        Retrieves the currently connected user object.
        :return: The user instance.
        :rtype: User
        """
        return self.user_profile