import socket
import threading
import time


class TriviaClient:
    LISTENING_PORT = 13117

    def __init__(self, server_ip, server_port, player_name):
        self.server_ip = server_ip
        self.server_port = server_port
        self.player_name = player_name

        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.broadcast_socket.bind(("", TriviaClient.LISTENING_PORT))
        print("Client started, listening for offer requests...")

    def connect_to_server(self):
        try:
            self.tcp_socket.connect((self.server_ip, self.server_tcp_port))
            self.tcp_socket.send((self.player_name + '\n').encode('utf-8'))
            print("Connected to the server.")

            threading.Thread(target=self.receive_question_messages).start()
            while True:
                time.sleep(1)


            # TODO: Add logic for handling keyboard input and sending answers to the server

        except Exception as e:
            print(f"Error connecting to the server: {e}")
            self.tcp_socket.close()

    def receive_question_messages(self):
        try:
            while True:
                client_socket, client_address = self.tcp_socket.recvfrom(1024)
                server_message = client_socket.decode('utf-8')
                print(server_message)
                input_answer = input()
                bool_answer = None
                if input_answer in ('T', 1, 'Y', 't', 'y'):
                    bool_answer = True
                elif input_answer in ('F', 0, 'N', 'f', 'n'):
                    bool_answer = False
                if bool_answer is not None:
                    self.tcp_socket.send(str(bool_answer).encode('utf-8'))
                time.sleep(1)
        except Exception as e:
            print(f"Error receiving messages: {e}")
        finally:
            self.broadcast_socket.close()

    def receive_offer_messages(self):
        try:
            while True:
                offer_message, server_address = self.broadcast_socket.recvfrom(1024)
                self.server_ip = server_address[0]
                if not offer_message:
                    break
                self.parse_offer(offer_message)
                print(f"Received offer from server '{self.server_name}' at address {server_address}, attempting to connect...")
                break
        except Exception as e:
            print(f"Error receiving messages: {e}")
        finally:
            self.broadcast_socket.close()

    def parse_offer(self, offer_message: bytes):
        if not self.valid_cookie(offer_message):
            return
        if not self.valid_message_type(offer_message):
            return
        self.server_name = self.parse_server_name(offer_message)
        self.server_tcp_port = self.parse_server_tcp_port(offer_message)

    def valid_cookie(self, offer_massage):
        return offer_massage[:4] == b'\xab\xcd\xdc\xba'

    def valid_message_type(self, offer_massage):
        return offer_massage[4] == 0x2

    def parse_server_name(self, offer_massage):
        decoded_string = offer_massage[5:37].decode('utf-8')
        return decoded_string.rstrip()

    def parse_server_tcp_port(self, offer_message):
        return int.from_bytes(offer_message[-2:], byteorder='big')


if __name__ == "__main__":
    # Replace these values with the actual server IP, port, and player name
    server_ip = "127.1.0.4"
    server_port = 5000
    player_name = "Alice"

    trivia_client = TriviaClient(server_ip, server_port, player_name)
    trivia_client.receive_offer_messages()
    trivia_client.connect_to_server()
