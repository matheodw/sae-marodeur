"""Gère la communication réseau entre le client (app PyQt) et le serveur.
Inclut l'envoi de commandes, la réception de données et le parsing des réponses.
"""
class ClientNetwork:
    def send_request(self, action, data=None):
        print("→ Envoi au serveur :", action, data)
        return {"status": "OK"}