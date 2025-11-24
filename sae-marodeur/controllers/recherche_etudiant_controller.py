# recherche_etudiant_controller.py
class RechercheEtudiantController:
    def __init__(self):
        from nomprojet.views.recherche_etudiant_view import RechercheEtudiantView
        self.view = RechercheEtudiantView()


    def show(self):
        self.view.show()