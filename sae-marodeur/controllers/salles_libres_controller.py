"""Gère l'affichage et la mise à jour des salles libres.
Appelle le serveur pour récupérer la liste en temps réel.
"""
class SallesLibresController:
    def __init__(self):
        from nomprojet.views.carte_salles_libres_view import CarteSallesLibresView
        self.view = CarteSallesLibresView()


    def show(self):
        self.view.show()