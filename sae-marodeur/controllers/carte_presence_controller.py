"""Contrôleur pour la Carte des présences.
Gère la transmission du profil et le chargement des données.
"""
import sys
import os

class CartePresenceController:
    def __init__(self, user_profile):
        # Sécurité pour les imports selon la structure du projet
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from views.carte_presence_view import CartePresenceView
        
        self.user_profile = user_profile
        
        # ON PASSE LE PROFIL : C'est ce qui répare ta sidebar
        self.view = CartePresenceView(profile=self.user_profile) 
        
        # Connexion des signaux spécifiques (si besoin)
        self.connect_signals()
        
        # Simulation de chargement de données
        self.load_initial_data()

    def connect_signals(self):
        """Connecte les signaux d'action de la vue."""
        # Les signaux go_to... sont gérés par le NavigationManager
        pass

    def load_initial_data(self):
        """Charge des données de test dans le tableau."""
        test_data = []
        self.view.load_presences(test_data)

    def show(self):
        """Affiche la vue."""
        self.view.show()