# client_network.py
class ClientNetwork:
    def send_request(self, action, data=None):
        print("→ Envoi au serveur :", action, data)
        return {"status": "OK"}