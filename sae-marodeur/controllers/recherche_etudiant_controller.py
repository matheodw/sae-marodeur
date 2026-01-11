"""Contrôleur chargé de la recherche d'étudiants.
Fait le lien entre la vue et la logique de recherche.
"""
import sys
import os

class RechercheEtudiantController:
    def __init__(self, user_profile):
        # On s'assure que le chemin est correct pour les imports
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from views.recherche_etudiant_view import RechercheEtudiantView
        
        self.user_profile = user_profile
        
        # IMPORTANT : On passe le profil à la vue ici
        self.view = RechercheEtudiantView(profile=self.user_profile)
        
        self.connect_signals()

    def connect_signals(self):
        """Connecte les signaux d'action (hors navigation gérée par NavigationManager)."""
        self.view.search_signal.connect(self.handle_search)

    def handle_search(self, query):
        """Logique de recherche (simulée pour le test)."""
        print(f"Recherche lancée pour : {query}")
        # Exemple de résultats fictifs
        results = []
        self.view.load_results(results)

    def show(self):
        self.view.show()