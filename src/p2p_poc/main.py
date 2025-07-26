import socket
import threading
import sys


class P2PChat:
    def __init__(self, host='0.0.0.0', port=55555):
        self.host = host
        self.port = port
        self.peers = []  # List of connected peers (host, port)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True

    def _start_server(self):
        """Run as server to accept incoming connections"""
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Listening on {self.host}:{self.port}")

        while self.running:
            client_socket, addr = self.server_socket.accept()
            print(f"Connected to {addr}")
            self.peers.append((addr[0], addr[1]))
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        """Handle messages from a connected peer"""
        while self.running:
            try:
                message = client_socket.recv(1024).decode()
                if not message:
                    break
                print(f"\n[Peer] {message}\n[You] ", end='')
            except:
                break
        client_socket.close()

    def connect_to_peer(self, peer_host, peer_port):
        """Initiate connection to another peer"""
        try:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect((peer_host, peer_port))
            self.peers.append((peer_host, peer_port))
            threading.Thread(target=self.handle_client, args=(peer_socket,)).start()
            print(f"Connected to {peer_host}:{peer_port}")
            return peer_socket
        except Exception as e:
            print(f"Connection failed: {e}")
            return None

    def send_message(self, message):
        """Send message to all connected peers"""
        for peer in self.peers.copy():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((peer[0], peer[1]))
                s.send(message.encode())
                s.close()
            except:
                print(f"Failed to send to {peer[0]}:{peer[1]}")
                self.peers.remove(peer)

    def start(self):
        """Start the P2P node"""
        # Start server component
        threading.Thread(target=self._start_server, daemon=True).start()

        # Connect to initial peer if specified
        if len(sys.argv) > 1:
            peer_host, peer_port = sys.argv[1].split(":")
            self.connect_to_peer(peer_host, int(peer_port))

        # User input handling
        while self.running:
            message = input("[You] ")
            if message.lower() == 'exit':
                self.running = False
                break
            self.send_message(message)


if __name__ == "__main__":
    node = P2PChat()
    node.start()