import time
from socket import *
import logging
import os

n = 0
my_set = {}
TARGET = 'd04863f100d59b3eb688a11f95b0ae60'
isDone = False

OG_FORMAT = '%(levelname)s | %(asctime)s | %(message)s'
LOG_LEVEL = logging.DEBUG
LOG_DIR = 'log'
LOG_FILE = os.path.join(LOG_DIR, 'client.log')

logging.basicConfig(filename=LOG_FILE, level=LOG_LEVEL, format=OG_FORMAT)


def handle_client1(address, complete_message, server_socket):
    """
    Handle client requests of type 'r'.

    Sends back the current value of n and updates my_set with timestamps.

    Args:
        address: The address of the client.
        complete_message: The complete message received from the client.
        server_socket: The UDP socket used to send responses.
    """
    global my_set, n
    logging.debug(f"Handling client1: {address}, message: {complete_message}")

    if bool(my_set) and my_set[next(iter(my_set))] <= time.time():
        temp = next(iter(my_set))
        my_set[temp] = time.time() + 3
        server_socket.sendto((str(temp) + '$' + TARGET + '!').encode(), address)
        logging.info(f"Sent response to {address}: {temp}$TARGET")
    else:
        server_socket.sendto((str(n) + '$' + TARGET + '!').encode(), address)
        logging.info(f"Sent response to {address}: {n}$TARGET")
        for i in range(int(complete_message)):
            my_set[n] = time.time() + 3
            n += 1


def handle_client2(complete_message):
    """
    Handle client requests of type 'f'.

    Removes an entry from my_set based on the complete message.

    Args:
        complete_message: The complete message received from the client.
    """
    global my_set
    index_to_remove = int(int(complete_message) / 1000)
    my_set.pop(index_to_remove, None)  # Use pop with a default to avoid KeyError
    logging.debug(f"Handled client2: Removed index {index_to_remove} from my_set.")


def handle_client3(complete_message):
    """
    Handle client requests of type 's'.

    Logs the complete message received.

    Args:
        complete_message: The complete message received from the client.
    """
    logging.info(f"Handled client3: complete message - {complete_message}")
    print(complete_message)


def handle_msg(server_socket):
    """
    Continuously handle incoming messages from clients.

    Process messages and calls the appropriate handler based on message type.

    Args:
        server_socket: The UDP socket used to receive messages.
    """
    while True:
        message_buffer = ""
        while True:
            data, address = server_socket.recvfrom(1024)
            message_buffer += data.decode()
            if message_buffer.endswith('!'):
                complete_message = message_buffer[:-1]
                break
        if complete_message[0] == 'r':
            complete_message = complete_message[1:]
            handle_client1(address, complete_message, server_socket)
        elif complete_message[0] == 'f':
            complete_message = complete_message[1:]
            handle_client2(complete_message)
        elif complete_message[0] == 's':
            complete_message = complete_message[1:]
            handle_client3(complete_message)
            break


def main():
    """
    Main function to set up the UDP server and handle messages.
    """
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(('127.0.0.1', 12000))
    logging.info("Server started and listening on port 12000.")
    handle_msg(serverSocket)


if __name__ == '__main__':
    assert n >= 0, "Counter n must not be negative."
    assert isinstance(my_set, dict), "my_set must be a dictionary."
    main()
