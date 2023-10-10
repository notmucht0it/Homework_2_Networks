"""
Kevin Monahan
Comp Sci 520 - Homework 2
10/10/23
"""

import socket
import sys
from os import popen

CLRF = '\r\n'
PORT = 25


def check_num(x, y):
    """Checks if returned response includes y"""
    if y in x:
        return True
    return False


def get_smtp_server(line):
    """Gets the mail server from the email address"""
    if "@" in line:
        temp = line.split("@", 1)[1]
        return temp.split(">", 1)[0]
    raise RuntimeError("Receiver email is not valid")


def send_mail(file_path):
    """Sends the email in a given file"""
    with open(file_path, encoding="utf-8") as file:
        file_contents = file.read()
    upper_parts = file_contents.split('\n', 3)
    # Specify the mail server and port number
    # Need to lookup recipient email server not sender
    system_read = popen("nslookup -q=MX " + get_smtp_server(upper_parts[1]))

    mailserver = system_read.read().split("mail exchanger = ", 1)[1]
    system_read.close()
    mailserver = mailserver.split("\n", 1)[0]
    # Create a socket and connect to the mail server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((mailserver, PORT))

    # Receive the connection greeting message from the server
    recv = client_socket.recv(1024)
    if not check_num(recv, b'220'):
        print("Failure")
        raise RuntimeError("Could not connect to mail server successfully")

    client_socket.send(b'HELO Server\r\n')
    recv = client_socket.recv(1024)
    if not check_num(recv, b'250'):
        raise RuntimeError("Could not say hello properly")

    # Send the MAIL FROM command and receive the server response
    mail_from_command = ('MAIL FROM: <' + upper_parts[0].split(" <", 1)[1]
                         + CLRF)
    client_socket.send(mail_from_command.encode())
    recv = client_socket.recv(1024)
    if not check_num(recv, b'250'):
        raise RuntimeError("Mail from user to accepted")
    # Send the RCPT TO command and receive the server response
    rcpt_to_command = 'RCPT TO: <' + upper_parts[1].split(" <", 1)[1] + CLRF
    client_socket.send(rcpt_to_command.encode())
    recv = client_socket.recv(1024)
    if not check_num(recv, b'250'):
        raise RuntimeError("Mail to user is not possible")
    # Send the DATA command and receive the server response
    data_command = 'DATA\r\n'
    client_socket.send(data_command.encode())
    recv = client_socket.recv(1024)
    if not check_num(recv, b'354'):
        raise RuntimeError("Issue with starting message")
    # Send the email message
    message = upper_parts[0] + CLRF
    message += upper_parts[1] + CLRF
    message += upper_parts[2] + CLRF + CLRF
    message += file_contents.split('\n\n', 1)[1] + CLRF
    message += '.\r\n'
    client_socket.send(message.encode())
    recv = client_socket.recv(1024)
    if not check_num(recv, b'250'):
        raise RuntimeError("Could not send mail")
    # Send the QUIT command and receive the server response
    client_socket.send(b'QUIT\r\n')
    recv = client_socket.recv(1024)
    if not check_num(recv, b'221'):
        print(recv)
        raise RuntimeError("Could not close connection to mail server")
    client_socket.close()


def main():
    """Runs the code"""
    args = sys.argv
    if len(args) == 1:
        return
    args.pop(0)
    for each in args:
        send_mail(each)


if __name__ == "__main__":
    main()
