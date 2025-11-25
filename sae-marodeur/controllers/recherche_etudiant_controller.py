"""Contrôleur chargé de la recherche d'étudiants.
Interroge la base de données via le serveur et met à jour la vue.
"""
class RechercheEtudiantController:
    def __init__(self):
        from nomprojet.views.recherche_etudiant_view import RechercheEtudiantView
        self.view = RechercheEtudiantView()


    def show(self):
        self.view.show()