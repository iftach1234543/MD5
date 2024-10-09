from socket import *
import logging
import os
import hashlib
import threading

clientSocket = socket(AF_INET, SOCK_DGRAM)
IP = '127.0.0.1'
PORT = 12000

LOG_FORMAT = '%(levelname)s | %(asctime)s | %(message)s'
LOG_LEVEL = logging.DEBUG
LOG_DIR = 'log'
LOG_FILE = os.path.join(LOG_DIR, 'lucky.log')


def check_md5(input_string, md5_string):
    """
    Compute the MD5 hash of the input string and compare it to the provided MD5 string.

    Args:
        input_string: The string to be hashed.
        md5_string: The MD5 hash to compare against.

    Returns:
        bool: True if the computed hash matches the provided hash, False otherwise.
    """
    hash_object = hashlib.md5(input_string.encode())
    computed_md5 = hash_object.hexdigest()
    return computed_md5 == md5_string


def md5_brute_force(target_hash, attempts, my_socket):
    """
    Performs brute force attempts on the MD5 hash.

    Args:
        target_hash: The target MD5 hash to crack.
        attempts: The number of attempts to add to the base value.
        my_socket: The socket used to send results to the server.
    """
    for i in range(1000):
        if check_md5(str((i + attempts)), target_hash):
            my_socket.sendto(('s' + str(i + attempts) + '!').encode(), (IP, PORT))
            return
    my_socket.sendto(('f' + str(attempts) + '!').encode(), (IP, PORT))


def handle_brute_force(target_md5, my_socket):
    """
    Starts brute force threads for each CPU core.

    Args:
        target_md5: A list containing the base value and the target hash.
        my_socket: The socket used to send results to the server.
    """
    temp = target_md5[0]
    for i in range(os.cpu_count()):
        target_md5[0] = (int(temp) + i) * 1000
        threading.Thread(target=md5_brute_force, args=(target_md5[1], target_md5[0], my_socket), daemon=True).start()


def send_message(my_socket):
    """
    Sends the number of CPU cores to the server and processes the response.

    Args:
        my_socket: The socket used to communicate with the server.
    """
    try:
        my_socket.sendto(('r' + str(os.cpu_count()) + '!').encode(), (IP, PORT))
        target_md5 = ""
        while True:
            msg, address = my_socket.recvfrom(1024)
            target_md5 += msg.decode()
            if target_md5.endswith('!'):
                target_md5 = target_md5[:-1]
                target_md5 = target_md5.split('$')
                break
        handle_brute_force(target_md5, my_socket)

    except socket.error as err:
        logging.error('Received socket error on client socket: ' + str(err))


def main():
    """
    Main function to initialize logging and send the initial message to the server.
    """
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    logging.basicConfig(format=LOG_FORMAT, filename=LOG_FILE, level=LOG_LEVEL)
    my_socket = socket(AF_INET, SOCK_DGRAM)

    try:
        send_message(my_socket)
    except socket.error as err:
        logging.error('Received socket error on client socket: ' + str(err))
    finally:
        my_socket.close()


if __name__ == '__main__':
    assert isinstance(clientSocket, socket), "clientSocket must be a socket instance."
    assert isinstance(LOG_DIR, str), "LOG_DIR must be a string."
    assert os.path.exists(LOG_DIR), "LOG_DIR must exist."
    main()
