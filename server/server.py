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
        self.sock: Optional[socket.socket] = None
        self.running = False
        self.database = Database()
        # Dictionnaire pour stocker les sessions utilisateurs (socket -> user_info)
        self.sessions: Dict[socket.socket, Dict[str, Any]] = {}
        # map action -> handler method
        self.handlers = {
            "login": self.handle_login,
            "logout": self.handle_logout,
            "get_presences": self.handle_get_presences,
            "get_presence_map": self.handle_get_presence_map,
            "get_salles_libres": self.handle_get_salles_libres,
            "search_etudiant": self.handle_search_etudiant,
            "get_all_users": self.handle_get_all_users,
            "create_user": self.handle_create_user,
            "update_user": self.handle_update_user,
            "delete_user": self.handle_delete_user,
        }

    def start(self):
        """Start listening for incoming connections."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        self.running = True
        print(f"Server listening on {self.host}:{self.port}")

        try:
            while self.running:
                client, addr = self.sock.accept()
                t = threading.Thread(target=self.handle_client, args=(client, addr), daemon=True)
                t.start()
        finally:
            self.stop()

    def stop(self):
        """Arrête le serveur."""
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            finally:
                self.sock = None
        print("Server stopped")

    def recv_exact(self, client: socket.socket, n: int) -> bytes:
        """Read exactly n bytes from client socket."""
        buf = b""
        while len(buf) < n:
            chunk = client.recv(n - len(buf))
            if not chunk:
                break
            buf += chunk
        return buf

    def handle_client(self, client: socket.socket, addr: tuple):
        """Handle a single client connection."""
        try:
            while True:
                length_b = self.recv_exact(client, 4)
                if len(length_b) != 4:
                    break

                length = int.from_bytes(length_b, byteorder='big')

                # Read the full JSON message
                body = self.recv_exact(client, length)
                if len(body) != length:
                    break

                try:
                    req = json.loads(body.decode("utf-8"))
                except Exception:
                    self.send_response(client, {"status": "error", "message": "invalid json"})
                    continue

                action = req.get("action")
                data = req.get("data", {})
                resp = self.process_request(client, action, data)
                self.send_response(client, resp)
        except Exception as e:
            print(f"client error {addr}: {e}")
        finally:
            if client in self.sessions:
                del self.sessions[client]
            client.close()

    def send_response(self, client: socket.socket, resp: Dict[str, Any]):
        """Send a JSON response prefixed with length."""
        try:
            b = json.dumps(resp).encode("utf-8")
            client.sendall(len(b).to_bytes(4, "big") + b)
        except Exception as e:
            print(f"send error: {e}")

    def process_request(self, client: socket.socket, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Route the action to the corresponding handler."""
        if not action:
            return {"status": "error", "message": "no action"}
        handler = self.handlers.get(action)
        if not handler:
            return {"status": "error", "message": f"unknown action {action}"}
        try:
            return handler(client, data)
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def is_authenticated(self, client: socket.socket) -> bool:
        """Return True if client has an authenticated session."""
        return client in self.sessions

    def get_user_session(self, client: socket.socket) -> Optional[Dict[str, Any]]:
        """Return the stored session for client or None."""
        return self.sessions.get(client)

    # Handlers
    def handle_login(self, client: socket.socket, data: Dict[str, Any]) -> Dict[str, Any]:
        """Authenticate a user and create a session.

        :param data: expects 'username' and 'password'
        :return: dict response
        """
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            return {"status": "error", "message": "username and password required"}
        user = self.database.authenticate_user(username, password)
        if not user:
            return {"status": "error", "message": "invalid credentials"}
        self.sessions[client] = {"user_id": user["id"], "username": user["username"], "role": user.get("role")}
        return {"status": "success", "user": user}

    def handle_logout(self, client: socket.socket, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove the client's session."""
        if client in self.sessions:
            del self.sessions[client]
        return {"status": "success"}

    def handle_get_presences(self, client: socket.socket, data: Dict[str, Any]) -> Dict[str, Any]:
        """Return current presences (requires auth)."""
        if not self.is_authenticated(client):
            return {"status": "error", "message": "authentication required"}
        return {"status": "success", "data": self.database.get_presences()}

    def handle_get_presence_map(self, client: socket.socket, data: Dict[str, Any]) -> Dict[str, Any]:
        """Return presence map (requires auth)."""
        if not self.is_authenticated(client):
            return {"status": "error", "message": "authentication required"}
        return {"status": "success", "data": self.database.get_presence_map()}

    def handle_get_salles_libres(self, client: socket.socket, data: Dict[str, Any]) -> Dict[str, Any]:
        """Return free rooms (requires auth)."""
        if not self.is_authenticated(client):
            return {"status": "error", "message": "authentication required"}
        return {"status": "success", "data": self.database.get_salles_libres()}

    def handle_search_etudiant(self, client: socket.socket, data: Dict[str, Any]) -> Dict[str, Any]:
        """Search students (requires auth)."""
        if not self.is_authenticated(client):
            return {"status": "error", "message": "authentication required"}
        query = data.get("query")
        if not query:
            return {"status": "error", "message": "query required"}
        return {"status": "success", "data": self.database.search_etudiant(query)}

    def handle_get_all_users(self, client: socket.socket, data: Dict[str, Any]) -> Dict[str, Any]:
        """Return all users (admin only)."""
        if not self.is_authenticated(client):
            return {"status": "error", "message": "authentication required"}
        session = self.get_user_session(client)
        if session.get("role") != "administration":
            return {"status": "error", "message": "permission denied"}
        return {"status": "success", "data": self.database.get_all_users()}

    def handle_create_user(self, client: socket.socket, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a user (admin only)."""
        if not self.is_authenticated(client):
            return {"status": "error", "message": "authentication required"}
        session = self.get_user_session(client)
        if session.get("role") != "administration":
            return {"status": "error", "message": "permission denied"}
        username = data.get("username")
        password = data.get("password")
        role = data.get("role")
        if not username or not password or not role:
            return {"status": "error", "message": "username, password and role required"}
        uid = self.database.create_user(username, password, role, nom=data.get("nom"), prenom=data.get("prenom"))
        if uid:
            return {"status": "success", "data": {"user_id": uid}}
        return {"status": "error", "message": "failed to create user"}

    def handle_update_user(self, client: socket.socket, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a user (admin only)."""
        if not self.is_authenticated(client):
            return {"status": "error", "message": "authentication required"}
        session = self.get_user_session(client)
        if session.get("role") != "administration":
            return {"status": "error", "message": "permission denied"}
        user_id = data.get("user_id")
        if not user_id:
            return {"status": "error", "message": "user_id required"}
        ok = self.database.update_user(user_id, data)
        return {"status": "success"} if ok else {"status": "error", "message": "update failed"}

    def handle_delete_user(self, client: socket.socket, data: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a user (admin only)."""
        if not self.is_authenticated(client):
            return {"status": "error", "message": "authentication required"}
        session = self.get_user_session(client)
        if session.get("role") != "administration":
            return {"status": "error", "message": "permission denied"}
        user_id = data.get("user_id")
        if not user_id:
            return {"status": "error", "message": "user_id required"}
        ok = self.database.delete_user(user_id)
        return {"status": "success"} if ok else {"status": "error", "message": "delete failed"}


# Run server
if __name__ == "__main__":
    s = Server(host="localhost", port=8888)
    try:
        s.start()
    except KeyboardInterrupt:
        print("Stopping server...")
        s.stop()
