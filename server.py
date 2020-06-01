import socket
import select

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 1234

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# allows to reconnect
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))

server_socket.listen()

socket_list = [server_socket]

clients = {}


def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            # client closed the connection
            return False
        message_length = int(message_header.decode('utf-8').strip())
        return {"header": message_header, "data": client_socket.recv(message_length)}
    except:
        return False

while True:
    read_sockets, _, exception_sockets = select.select(socket_list, [], socket_list)
    # (read_list, write_list, error_list)
    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            # Someone just connected
            client_socket, client_address = server_socket.accept()
            
            user = receive_message(client_socket)
            if user is False:
                continue
            socket_list.append(client_socket)
            clients[client_socket] = user
            print('ACCEPTED new connection from {}:{} username {}'.format(client_address[0], client_address[1], user['data'].decode('utf-8')))
        else:
            message = receive_message(notified_socket)
            if message is False:
                print('Closed connection from {}'.format(clients[notified_socket]['data'].decode('utf-8')))
                socket_list.remove(notified_socket)
                del clients[notified_socket]
                continue
            user = clients[notified_socket]
            print('RECEIVED message from {}: {}'.format(user['data'].decode('utf-8'), message['data'].decode('utf-8')))
            
            for client_socket in clients:
                if client_socket is not notified_socket:
                    client_socket.send(user['header']+user['data']+message['header']+message['data'])


    for notified_socket in exception_sockets:
        socket_list.remove(notified_socket)
        del clients[notified_socket]




