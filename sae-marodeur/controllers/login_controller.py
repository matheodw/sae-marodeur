"""Gère la logique d'authentification utilisateur.
Interagit avec le modèle User et la vue LoginView.
"""
class LoginController:
    def __init__(self):
        from nomprojet.views.login_view import LoginView
        self.view = LoginView()
        self.view.login_signal.connect(self.authenticate)


    def authenticate(self, username, password):
        print("Authentification tentative...", username)
        # Appel réseau → serveur
        # Ensuite ouvrir le bon HomeController


    def show(self):
        self.view.show()