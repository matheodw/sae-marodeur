class CartePresenceController:
    def __init__(self, user_profile):
        from views.carte_presence_view import CartePresenceView
        self.view = CartePresenceView(profile=user_profile)
        self.load_initial_data()

    def load_initial_data(self):
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
        self.view.show()
