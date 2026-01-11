"""Serveur principal du projet.
Gère les connexions clients, interprète les commandes et renvoie les réponses.
"""
import socket
import json
import threading
from typing import Dict, Any, Optional
from database import Database


class Server:
    """Serveur TCP qui gère les connexions clients et traite les requêtes."""
    
    def __init__(self, host: str = "localhost", port: int = 8888):
        """
        Initialise le serveur.
        
        Args:
            host: Adresse IP d'écoute (par défaut localhost)
            port: Port d'écoute (par défaut 8888)
        """
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.running = False
        self.database = Database()
        # Dictionnaire pour stocker les sessions utilisateurs (socket -> user_info)
        self.sessions: Dict[socket.socket, Dict[str, Any]] = {}
    
    def start(self):
        """Démarre le serveur et écoute les connexions."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.running = True
            
            print(f"Serveur démarré sur {self.host}:{self.port}")
            
            while self.running:
                try:
                    client_socket, address = self.socket.accept()
                    print(f"Nouvelle connexion depuis {address}")
                    
                    # Créer un thread pour gérer ce client
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address),
                        daemon=True
                    )
                    client_thread.start()
                    
                except socket.error as e:
                    if self.running:
                        print(f"Erreur lors de l'acceptation: {e}")
        except Exception as e:
            print(f"Erreur lors du démarrage du serveur: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Arrête le serveur."""
        self.running = False
        if self.socket:
            self.socket.close()
        print("Serveur arrêté")
    
    def handle_client(self, client_socket: socket.socket, address: tuple):
        """
        Gère la communication avec un client.
        
        Args:
            client_socket: Socket du client
            address: Adresse du client
        """
        try:
            while self.running:
                # Recevoir la longueur du message (4 bytes)
                length_bytes = client_socket.recv(4)
                if not length_bytes or len(length_bytes) != 4:
                    break
                
                message_length = int.from_bytes(length_bytes, byteorder='big')
                
                # Recevoir le message JSON complet
                message_data = b""
                while len(message_data) < message_length:
                    chunk = client_socket.recv(message_length - len(message_data))
                    if not chunk:
                        break
                    message_data += chunk
                
                if len(message_data) != message_length:
                    break
                
                # Parser le JSON
                try:
                    request = json.loads(message_data.decode('utf-8'))
                except json.JSONDecodeError as e:
                    self._send_response(client_socket, {
                        "status": "error",
                        "message": f"Erreur de parsing JSON: {e}"
                    })
                    continue
                
                # Traiter la requête
                action = request.get("action")
                data = request.get("data", {})
                
                # Router vers la bonne fonction
                response = self.process_request(client_socket, action, data)
                
                # Envoyer la réponse
                self._send_response(client_socket, response)
                
        except Exception as e:
            print(f"Erreur avec le client {address}: {e}")
        finally:
            # Nettoyer la session
            if client_socket in self.sessions:
                del self.sessions[client_socket]
            client_socket.close()
            print(f"Connexion fermée avec {address}")
    
    def _send_response(self, client_socket: socket.socket, response: Dict[str, Any]):
        """
        Envoie une réponse au client.
        
        Args:
            client_socket: Socket du client
            response: Dictionnaire de réponse à envoyer
        """
        try:
            message = json.dumps(response).encode('utf-8')
            message_length = len(message).to_bytes(4, byteorder='big')
            client_socket.sendall(message_length + message)
        except Exception as e:
            print(f"Erreur lors de l'envoi de la réponse: {e}")
    
    def process_request(self, client_socket: socket.socket, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Traite une requête et retourne la réponse.
        
        Args:
            client_socket: Socket du client
            action: Action demandée
            data: Données de la requête
            
        Returns:
            Dictionnaire de réponse
        """
        # Router selon l'action
        if action == "login":
            return self.handle_login(client_socket, data)
        elif action == "logout":
            return self.handle_logout(client_socket, data)
        elif action == "get_presences":
            return self.handle_get_presences(client_socket, data)
        elif action == "get_presence_map":
            return self.handle_get_presence_map(client_socket, data)
        elif action == "get_salles_libres":
            return self.handle_get_salles_libres(client_socket, data)
        elif action == "get_salles_libres_map":
            return self.handle_get_salles_libres_map(client_socket, data)
        elif action == "search_etudiant":
            return self.handle_search_etudiant(client_socket, data)
        elif action == "get_etudiant_location":
            return self.handle_get_etudiant_location(client_socket, data)
        elif action == "get_all_users":
            return self.handle_get_all_users(client_socket, data)
        elif action == "create_user":
            return self.handle_create_user(client_socket, data)
        elif action == "update_user":
            return self.handle_update_user(client_socket, data)
        elif action == "delete_user":
            return self.handle_delete_user(client_socket, data)
        else:
            return {
                "status": "error",
                "message": f"Action inconnue: {action}"
            }
    
    def is_authenticated(self, client_socket: socket.socket) -> bool:
        """Vérifie si le client est authentifié."""
        return client_socket in self.sessions
    
    def get_user_session(self, client_socket: socket.socket) -> Optional[Dict[str, Any]]:
        """Récupère la session utilisateur."""
        return self.sessions.get(client_socket)
    
    # ========== HANDLERS POUR CHAQUE ACTION ==========
    
    def handle_login(self, client_socket: socket.socket, data: Dict[str, Any]) -> Dict[str, Any]:
        """Gère l'authentification d'un utilisateur."""
        username = data.get("username")
        password = data.get("password")
        
        if not username or not password:
            return {
                "status": "error",
                "message": "Username et password requis"
            }
        
        # Vérifier les identifiants dans la base de données
        user = self.database.authenticate_user(username, password)
        
        if user:
            # Créer une session
            self.sessions[client_socket] = {
                "user_id": user.get("id"),
                "username": user.get("username"),
                "role": user.get("role")
            }
            return {
                "status": "success",
                "user": {
                    "id": user.get("id"),
                    "username": user.get("username"),
                    "role": user.get("role"),
                    "nom": user.get("nom"),
                    "prenom": user.get("prenom")
                }
            }
        else:
            return {
                "status": "error",
                "message": "Identifiants invalides"
            }
    
    def handle_logout(self, client_socket: socket.socket, data: Dict[str, Any]) -> Dict[str, Any]:
        """Gère la déconnexion d'un utilisateur."""
        if client_socket in self.sessions:
            del self.sessions[client_socket]
        return {"status": "success", "message": "Déconnexion réussie"}
    
    def handle_get_presences(self, client_socket: socket.socket, data: Dict[str, Any]) -> Dict[str, Any]:
        """Récupère la liste des présences."""
        if not self.is_authenticated(client_socket):
            return {"status": "error", "message": "Authentification requise"}
        
        presences = self.database.get_presences()
        return {
            "status": "success",
            "data": presences
        }
    
    def handle_get_presence_map(self, client_socket: socket.socket, data: Dict[str, Any]) -> Dict[str, Any]:
        """Récupère la carte des présences pour affichage."""
        if not self.is_authenticated(client_socket):
            return {"status": "error", "message": "Authentification requise"}
        
        presence_map = self.database.get_presence_map()
        return {
            "status": "success",
            "data": presence_map
        }
    
    def handle_get_salles_libres(self, client_socket: socket.socket, data: Dict[str, Any]) -> Dict[str, Any]:
        """Récupère la liste des salles libres."""
        if not self.is_authenticated(client_socket):
            return {"status": "error", "message": "Authentification requise"}
        
        salles = self.database.get_salles_libres()
        return {
            "status": "success",
            "data": salles
        }
    
    def handle_get_salles_libres_map(self, client_socket: socket.socket, data: Dict[str, Any]) -> Dict[str, Any]:
        """Récupère la carte des salles libres pour affichage."""
        if not self.is_authenticated(client_socket):
            return {"status": "error", "message": "Authentification requise"}
        
        salles_map = self.database.get_salles_libres_map()
        return {
            "status": "success",
            "data": salles_map
        }
    
    def handle_search_etudiant(self, client_socket: socket.socket, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recherche un étudiant."""
        if not self.is_authenticated(client_socket):
            return {"status": "error", "message": "Authentification requise"}
        
        query = data.get("query", "")
        if not query:
            return {"status": "error", "message": "Query requise"}
        
        results = self.database.search_etudiant(query)
        return {
            "status": "success",
            "data": results
        }
    
    def handle_get_etudiant_location(self, client_socket: socket.socket, data: Dict[str, Any]) -> Dict[str, Any]:
        """Récupère la localisation d'un étudiant."""
        if not self.is_authenticated(client_socket):
            return {"status": "error", "message": "Authentification requise"}
        
        etudiant_id = data.get("etudiant_id")
        if not etudiant_id:
            return {"status": "error", "message": "etudiant_id requis"}
        
        location = self.database.get_etudiant_location(etudiant_id)
        return {
            "status": "success",
            "data": location
        }
    
    def handle_get_all_users(self, client_socket: socket.socket, data: Dict[str, Any]) -> Dict[str, Any]:
        """Récupère tous les utilisateurs (admin uniquement)."""
        if not self.is_authenticated(client_socket):
            return {"status": "error", "message": "Authentification requise"}
        
        session = self.get_user_session(client_socket)
        if session.get("role") != "administration":
            return {"status": "error", "message": "Permissions insuffisantes"}
        
        users = self.database.get_all_users()
        return {
            "status": "success",
            "data": users
        }
    
    def handle_create_user(self, client_socket: socket.socket, data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée un utilisateur (admin uniquement)."""
        if not self.is_authenticated(client_socket):
            return {"status": "error", "message": "Authentification requise"}
        
        session = self.get_user_session(client_socket)
        if session.get("role") != "administration":
            return {"status": "error", "message": "Permissions insuffisantes"}
        
        username = data.get("username")
        password = data.get("password")
        role = data.get("role")
        
        if not username or not password or not role:
            return {"status": "error", "message": "username, password et role requis"}
        
        user_id = self.database.create_user(
            username=username,
            password=password,
            role=role,
            nom=data.get("nom"),
            prenom=data.get("prenom")
        )
        
        if user_id:
            return {
                "status": "success",
                "message": "Utilisateur créé avec succès",
                "data": {"user_id": user_id}
            }
        else:
            return {
                "status": "error",
                "message": "Erreur lors de la création de l'utilisateur"
            }
    
    def handle_update_user(self, client_socket: socket.socket, data: Dict[str, Any]) -> Dict[str, Any]:
        """Modifie un utilisateur (admin uniquement)."""
        if not self.is_authenticated(client_socket):
            return {"status": "error", "message": "Authentification requise"}
        
        session = self.get_user_session(client_socket)
        if session.get("role") != "administration":
            return {"status": "error", "message": "Permissions insuffisantes"}
        
        user_id = data.get("user_id")
        if not user_id:
            return {"status": "error", "message": "user_id requis"}
        
        success = self.database.update_user(user_id, data)
        
        if success:
            return {
                "status": "success",
                "message": "Utilisateur modifié avec succès"
            }
        else:
            return {
                "status": "error",
                "message": "Erreur lors de la modification de l'utilisateur"
            }
    
    def handle_delete_user(self, client_socket: socket.socket, data: Dict[str, Any]) -> Dict[str, Any]:
        """Supprime un utilisateur (admin uniquement)."""
        if not self.is_authenticated(client_socket):
            return {"status": "error", "message": "Authentification requise"}
        
        session = self.get_user_session(client_socket)
        if session.get("role") != "administration":
            return {"status": "error", "message": "Permissions insuffisantes"}
        
        user_id = data.get("user_id")
        if not user_id:
            return {"status": "error", "message": "user_id requis"}
        
        success = self.database.delete_user(user_id)
        
        if success:
            return {
                "status": "success",
                "message": "Utilisateur supprimé avec succès"
            }
        else:
            return {
                "status": "error",
                "message": "Erreur lors de la suppression de l'utilisateur"
            }


# Script pour lancer le serveur
if __name__ == "__main__":
    server = Server(host="localhost", port=8888)
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nArrêt du serveur...")
        server.stop()