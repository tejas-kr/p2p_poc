# chat_server.py
import socket
import threading
import time


class ChatServer:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.clients = []  # List to store connected clients
        self.nicknames = []  # List to store client nicknames

    def broadcast(self, message, sender_client=None):
        """Send message to all connected clients except sender"""
        for client in self.clients:
            if client != sender_client:
                try:
                    client.send(message)
                except:
                    # If sending fails, remove the client
                    self.remove_client(client)

    def remove_client(self, client):
        """Remove a client from the server"""
        if client in self.clients:
            index = self.clients.index(client)
            self.clients.remove(client)
            nickname = self.nicknames[index]
            self.nicknames.remove(nickname)

            # Notify other clients
            self.broadcast(f"{nickname} left the chat!".encode('ascii'))
            client.close()
            print(f"[SERVER] {nickname} disconnected")

    def handle_client(self, client):
        """Handle messages from a client"""
        while True:
            try:
                # Receive message from client
                message = client.recv(1024)
                if message:
                    # Broadcast message to all other clients
                    self.broadcast(message, client)
                else:
                    # Empty message means client disconnected
                    self.remove_client(client)
                    break
            except:
                # Error occurred, remove client
                self.remove_client(client)
                break

    def start_server(self):
        """Start the chat server"""
        # Create socket
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen()

        print(f"[SERVER] Chat server is running on {self.host}:{self.port}")
        print("[SERVER] Waiting for clients to connect...")

        while True:
            try:
                # Accept new client connection
                client, address = server.accept()
                print(f"[SERVER] Connected with {str(address)}")

                # Request nickname from client
                client.send("NICK".encode('ascii'))
                nickname = client.recv(1024).decode('ascii')

                # Add client to lists
                self.nicknames.append(nickname)
                self.clients.append(client)

                print(f"[SERVER] Nickname of client is {nickname}")

                # Broadcast that new client joined
                self.broadcast(f"{nickname} joined the chat!".encode('ascii'))
                client.send("Connected to the server!".encode('ascii'))

                # Start handling thread for client
                thread = threading.Thread(target=self.handle_client, args=(client,))
                thread.daemon = True
                thread.start()

            except KeyboardInterrupt:
                print("\n[SERVER] Server shutting down...")
                break
            except Exception as e:
                print(f"[SERVER] Error: {e}")


if __name__ == "__main__":
    server = ChatServer()
    server.start_server()
