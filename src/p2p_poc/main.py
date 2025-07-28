import socket
import threading
import sys


class P2PChat:
    def __init__(self, host='0.0.0.0', port=0):  # Default port=0 (OS chooses)
        self.host = host
        self.port = port
        self.peers = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True

        # Enable address reuse
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def _start_server(self):
        self.server_socket.bind((self.host, self.port))
        # Update port if OS assigned it
        self.port = self.server_socket.getsockname()[1]
        self.server_socket.listen(5)
        print(f"Listening on {self.host}:{self.port}")

        while self.running:
            client_socket, addr = self.server_socket.accept()
            print(f"Connected to {addr}")
            self.peers.append((addr[0], addr[1]))
            threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()

    def handle_client(self, client_socket):
        while self.running:
            try:
                message = client_socket.recv(1024).decode()
                if not message:
                    break
                print(f"\n[Peer] {message}\n[You] ", end='', flush=True)
            except:
                break
        client_socket.close()

    def connect_to_peer(self, peer_host, peer_port):
        try:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect((peer_host, peer_port))
            self.peers.append((peer_host, peer_port))
            threading.Thread(target=self.handle_client, args=(peer_socket,), daemon=True).start()
            print(f"Connected to {peer_host}:{peer_port}")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def send_message(self, message):
        for peer in self.peers.copy():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((peer[0], peer[1]))
                s.send(message.encode())
                s.close()
            except:
                print(f"ⓧ Lost connection to {peer[0]}:{peer[1]}")
                self.peers.remove(peer)

    def start(self):
        # Start server component
        server_thread = threading.Thread(target=self._start_server, daemon=True)
        server_thread.start()

        # Allow time for server to bind
        threading.Event().wait(0.1)

        # Connect to peer if specified
        if len(sys.argv) > 2:
            peer_host, peer_port = sys.argv[2].split(":")
            self.connect_to_peer(peer_host, int(peer_port))

        # User interface
        print("\nCommands:\n  /connect <IP>:<PORT> - Connect to new peer\n  /exit - Quit\n")
        while self.running:
            try:
                user_input = input("[You] ")
                if user_input.lower() == '/exit':
                    self.running = False
                    break
                elif user_input.startswith('/connect '):
                    _, address = user_input.split(' ', 1)
                    peer_host, peer_port = address.split(":")
                    self.connect_to_peer(peer_host, int(peer_port))
                else:
                    self.send_message(user_input)
            except KeyboardInterrupt:
                self.running = False
                break

        print("Shutting down...")
        self.server_socket.close()


if __name__ == "__main__":
    port = 0  # Let OS choose port by default
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    node = P2PChat(port=port)
    node.start()