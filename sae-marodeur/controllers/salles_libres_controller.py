# salles_libres_controller.py
class SallesLibresController:
    def __init__(self):
        from nomprojet.views.carte_salles_libres_view import CarteSallesLibresView
        self.view = CarteSallesLibresView()


    def show(self):
        self.view.show()