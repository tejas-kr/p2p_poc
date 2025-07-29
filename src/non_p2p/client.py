# chat_client.py
import socket
import threading


class ChatClient:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.nickname = input("Choose a nickname: ")
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def receive_messages(self):
        """Continuously receive messages from server"""
        while True:
            try:
                message = self.client.recv(1024).decode('ascii')

                # Server requesting nickname
                if message == 'NICK':
                    self.client.send(self.nickname.encode('ascii'))
                else:
                    print(message)

            except:
                # Error occurred, close connection
                print("[CLIENT] An error occurred. Disconnecting...")
                self.client.close()
                break

    def send_messages(self):
        """Send messages to server"""
        while True:
            try:
                message = f"{self.nickname}: {input('')}"
                self.client.send(message.encode('ascii'))
            except:
                print("[CLIENT] Connection lost.")
                self.client.close()
                break

    def start_client(self):
        """Connect to server and start messaging"""
        try:
            # Connect to server
            self.client.connect((self.host, self.port))
            print(f"[CLIENT] Connected to chat server at {self.host}:{self.port}")
            print("Type your messages below (Ctrl+C to quit):")

            # Start receiving thread
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()

            # Start sending messages
            self.send_messages()

        except KeyboardInterrupt:
            print("\n[CLIENT] Disconnecting...")
            self.client.close()
        except Exception as e:
            print(f"[CLIENT] Error connecting to server: {e}")


if __name__ == "__main__":
    client = ChatClient()
    client.start_client()
