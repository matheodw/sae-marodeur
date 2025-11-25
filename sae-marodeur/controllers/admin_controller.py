"""Gère la logique métier pour l'administration des comptes.
Inclut la communication entre la vue AdminComptes et les modèles associés.
"""
class AdminController:
    def __init__(self):
        from nomprojet.views.admin_comptes_view import AdminComptesView
        self.view = AdminComptesView()


    def show(self):
        self.view.show()