import socket
import threading


class TriviaClient:
    def __init__(self, server_ip, server_port, player_name):
        self.server_ip = server_ip
        self.server_port = server_port
        self.player_name = player_name
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def connect_to_server(self):
        try:
            self.client_socket.connect((self.server_ip, self.server_port))
            self.client_socket.send((self.player_name + '\n').encode('utf-8'))
            print("Connected to the server.")

            threading.Thread(target=self.receive_messages, daemon=True).start()

            # TODO: Add logic for handling keyboard input and sending answers to the server

        except Exception as e:
            print(f"Error connecting to the server: {e}")
            self.client_socket.close()

    def receive_messages(self):
        try:
            while True:
                offer_message, server_address = self.broadcast_socket.recvfrom(1024)
                if not offer_message:
                    break
                print(offer_message.decode('utf-8'))
        except Exception as e:
            print(f"Error receiving messages: {e}")
        finally:
            self.broadcast_socket.close()


if __name__ == "__main__":
    # Replace these values with the actual server IP, port, and player name
    server_ip = "127.0.0.1"
    server_port = 12345
    player_name = "Alice"

    trivia_client = TriviaClient(server_ip, server_port, player_name)
    trivia_client.receive_messages()
    trivia_client.connect_to_server()
