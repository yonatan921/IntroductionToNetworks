import socket
import threading
import time
import random

SERVER_NAME = "TrivYos"
SERVER_IP_ADDRESS = '127.1.0.4'
SERVER_TCP_PORT = 5000

class TriviaServer:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((SERVER_IP_ADDRESS, SERVER_TCP_PORT))  # Binding to 0.0.0.0 allows connections from any IP
        self.server_socket.listen(5)
        self.players = []
        self.questions = [
            {"question": "Aston Villa's current manager is Pep Guardiola", "answer": False},
            {"question": "Aston Villa's mascot is a lion named Hercules", "answer": True},
            # Add more questions as needed
        ]
        self.current_question = None
        self.lock = threading.Lock()
        self.game_active = False

    def udp_broadcast(self):
        UDP_IP = '255.255.255.255'
        UDP_PORT = 13117
        offer_message = b'\xab\xcd\xdc\xba' + b'\x02' + b'TriviYos'.ljust(32) + SERVER_TCP_PORT.to_bytes(2, 'big')
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        broadcast_socket.bind((SERVER_IP_ADDRESS, UDP_PORT))
        print(f"Server started, listening on IP address {SERVER_IP_ADDRESS}")
        try:
            while not self.game_active:
                broadcast_socket.sendto(offer_message, (UDP_IP, UDP_PORT))
                time.sleep(1)
        finally:
            broadcast_socket.close()

    # def broadcast_offer(self):
    #     offer_message = b'\xab\xcd\xdc\xba' + b'\x02' + b'TriviYos'.ljust(32) + self.server_port.to_bytes(2, 'big')
    #     broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #     broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    #     # broadcast_socket.bind(('172.1.0.4', self.server_port))
    #     # broadcast_socket.listen(5)
    #     print("Server started, listening on IP address ___")
    #
    #
    #     try:
    #         while not self.game_active:
    #             broadcast_socket.sendto(offer_message, ('<broadcast>', 13117))
    #             time.sleep(1)
    #     finally:
    #         broadcast_socket.close()

    def handle_client(self, client_socket, player_name):
        try:
            # Handle client connection and game logic here
            pass
        except Exception as e:
            print(f"Error handling client {player_name}: {e}")
        finally:
            client_socket.close()

    def start_game(self):
        self.game_active = True
        # Send welcome message to clients
        welcome_message = f"Welcome to the {SERVER_NAME} server, " \
                          f"where we answer trivia questions about Aston Villa FC.\n"
        for i, player in enumerate(self.players, start=1):
            welcome_message += f"Player {i}: {player['name']}\n"
        welcome_message += "==\n"

        # Select a random question
        self.current_question = random.choice(self.questions)
        welcome_message += f"True or false: {self.current_question['question']}"
        print(welcome_message)

        # Broadcast the welcome message to all clients
        for player in self.players:
            player['socket'].send(welcome_message.encode('utf-8'))

        # TODO: Implement game logic here

    def run(self):
        threading.Thread(target=self.udp_broadcast).start()

        try:
            while True:
                client_socket, addr = self.server_socket.accept()
                player_name = client_socket.recv(1024).decode('utf-8').strip()

                with self.lock:
                    if not self.game_active:
                        self.players.append({'name': player_name, 'socket': client_socket})
                        print(f"Player {player_name} connected from {addr}")

                        if len(self.players) == 1:
                            threading.Thread(target=self.start_game).start()
                    else:
                        client_socket.send("Game in progress. Try again later.".encode('utf-8'))
                        client_socket.close()
        except KeyboardInterrupt:
            pass
        finally:
            self.server_socket.close()


if __name__ == "__main__":
    trivia_server = TriviaServer()
    # trivia_server.broadcast_offer()
    trivia_server.run()
