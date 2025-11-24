# admin_controller.py
class AdminController:
    def __init__(self):
        from nomprojet.views.admin_comptes_view import AdminComptesView
        self.view = AdminComptesView()


    def show(self):
        self.view.show()