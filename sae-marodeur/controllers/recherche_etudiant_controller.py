"""
Contrôleur chargé de la recherche d'étudiants.
Fait le lien entre la vue RechercheEtudiantView et la base de données.
"""

import os
import sys

from views.recherche_etudiant_view import RechercheEtudiantView


class RechercheEtudiantController:
    """
    Contrôleur de la recherche d'étudiants.
    """

    def __init__(self, user_profile):
        """
        Initialise le contrôleur et la vue associée.
        """
        self.user_profile = user_profile
        self.view = RechercheEtudiantView(profile=self.user_profile)

        self.connect_signals()

    def connect_signals(self):
        """
        Connecte les signaux de la vue aux méthodes du contrôleur.
        """
        self.view.search_signal.connect(self.handle_search)

    def handle_search(self, query):
        """
        Lance une recherche d'étudiants dans la base de données.
        """
        print(f"Recherche lancée pour : {query}")

        try:
            from server.database import Database
            db = Database()

            raw = db.search_etudiant(query)
            print("Résultats DB :", raw)

            results = [
                {
                    "nom": r.get("nom", r.get("nom_complet", "Inconnu")),
                    "salle": r.get("salle", "Non trouvé")
                }
                for r in (raw or [])
            ]

        except Exception as e:
            print(f"Erreur recherche_etudiant: {e}")
            results = []

        self.view.load_results(results)

    def show(self):
        """
        Affiche la vue.
        """
        self.view.show()
