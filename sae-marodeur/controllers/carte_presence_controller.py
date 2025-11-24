# carte_presence_controller.py
class CartePresenceController:
    def __init__(self):
        from nomprojet.views.carte_presence_view import CartePresenceView
        self.view = CartePresenceView()


    def load_data(self):
        pass


    def show(self):
        self.view.show()