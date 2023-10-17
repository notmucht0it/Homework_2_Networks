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


def creat_message(from_part, to_part, subject_part, mes):
    """Creates the email message which takes a body,
     subject, sender, and receiver"""
    message = from_part + CLRF
    message += to_part + CLRF
    message += subject_part + CLRF + CLRF
    message += mes + CLRF + "." + CLRF
    return message


def connect_to_server(mail_url):
    """Establishes a socket with connect to mail server located at mail_url"""
    system_read = popen("nslookup -q=MX " + get_smtp_server(mail_url))
    mailserver = system_read.read().split("mail exchanger = ", 1)
    if len(mailserver) == 1:
        raise RuntimeError("Server did not return information "
                           "necessary for the program")
    mailserver = mailserver[1]
    system_read.close()
    mailserver = mailserver.split("\n", 1)[0]
    # Create a socket and connect to the mail server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((mailserver, PORT))
    recv = client_socket.recv(1024)
    if not check_num(recv, b'220'):
        raise RuntimeError("Could not connect to mail server successfully")
    return client_socket


def read_file(file_path):
    """Reads the contents of a given file"""
    with open(file_path, encoding="utf-8") as file:
        return file.read()


def check_email_formatting(email):
    """Checks the formatting of the email to ensure it matches
    how emails are being sent in this program"""
    if len(email) == 4:
        if ("From:" in email[0] and
                "To:" in email[1] and
                "Subject:" in email[2]):
            return
    raise RuntimeError("Email was not properly formatted")


def send_mail(file_path):
    """Sends the email in a given file"""
    file_contents = read_file(file_path)
    upper_parts = file_contents.split('\n', 3)

    # Checks email formatting returning nothing if properly formatted
    check_email_formatting(upper_parts)
    val = '\n\n' in file_contents
    if not val:
        raise RuntimeError("Email is not formatted correctly")
    # Connects to the server
    client_socket = connect_to_server(upper_parts[1])

    # Sends hello to the server
    client_socket.send(b'HELO Server\r\n')
    recv = client_socket.recv(1024)
    if not check_num(recv, b'250'):
        raise RuntimeError(recv)

    # Send the MAIL FROM command and receive the server response
    mail_from_command = ('MAIL FROM: <' + upper_parts[0].split(" <", 1)[1]
                         + CLRF)
    client_socket.send(mail_from_command.encode())
    recv = client_socket.recv(1024)
    if not check_num(recv, b'250'):
        raise RuntimeError(recv)
    # Send the RCPT TO command and receive the server response
    rcpt_to_command = 'RCPT TO: <' + upper_parts[1].split(" <", 1)[1] + CLRF
    client_socket.send(rcpt_to_command.encode())
    recv = client_socket.recv(1024)
    if not check_num(recv, b'250'):
        raise RuntimeError(recv)
    # Send the DATA command and receive the server response
    client_socket.send(b'DATA\r\n')
    recv = client_socket.recv(1024)
    if not check_num(recv, b'354'):
        raise RuntimeError(recv)
    # Send the email message
    message = creat_message(upper_parts[0],
                            upper_parts[1],
                            upper_parts[2],
                            file_contents.split('\n\n', 1)[1])
    client_socket.send(message.encode())
    recv = client_socket.recv(1024)
    if not check_num(recv, b'250'):
        raise RuntimeError(recv)
    # Send the QUIT command and receive the server response
    client_socket.send(b'QUIT\r\n')
    recv = client_socket.recv(1024)
    if not check_num(recv, b'221'):
        print(recv)
        raise RuntimeError(recv)
    client_socket.close()


args = sys.argv
if len(args) != 1:
    args.pop(0)
    for each in args:
        send_mail(each)
