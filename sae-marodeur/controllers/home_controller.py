# home_controller.py
class HomeController:
    def __init__(self, user_profile):
        from nomprojet.views.home_view import HomeView
        self.view = HomeView(user_profile)
        self.view.go_to_presence_signal.connect(self.open_presence)


    def open_presence(self):
        pass


    def show(self):
        self.view.show()