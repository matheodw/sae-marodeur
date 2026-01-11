class CartePresenceController:
    """
    Controller responsible for managing the logic between the presence database 
    and the Presence Card view.

    This class follows the MVC pattern by fetching data from the Database 
    and formatting it for the CartePresenceView.

    :param user_profile: The profile object containing the current user's information.
    :type user_profile: object
    """

    def __init__(self, user_profile):
        """
        Initializes the controller, creates the view instance, and loads data.

        Note:
            Uses local imports for 'CartePresenceView' to prevent circular dependencies.
        """
        from views.carte_presence_view import CartePresenceView
        self.view = CartePresenceView(profile=user_profile)
        self.load_initial_data()

    def load_initial_data(self):
        """
        Fetches presence data from the database and updates the view.

        Process:
            1. Connects to the Database.
            2. Maps raw database keys ('nom_complet', 'salle') to view-friendly keys.
            3. In case of failure, loads hardcoded mock data to ensure UI stability.

        :raises Exception: Captures any database connection or parsing errors.
        """
        try:
            from server.database import Database
            db = Database()
            presences = db.get_presences()

            print("Présences DB :", presences)

            data = []
            for p in presences:
                data.append({
                    "nom": p.get("nom_complet", "Inconnu"),
                    "salle": p.get("salle", "N/A"),
                    "statut": "Présent"
                })

            self.view.load_presences(data)

        except Exception as e:
            print("Erreur carte présence :", e)
            self.view.load_presences([
                {"nom": "Dupont Jean", "salle": "A101", "statut": "Présent"},
                {"nom": "Martin Claire", "salle": "B201", "statut": "Présent"}
            ])

    def show(self):
        """
        Displays the presence card view to the user.
        """
        self.view.show()
