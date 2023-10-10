import socket
import sys
from os import popen


def check250(x):
    if b"250" in x:
        return True
    return False


def get_smtp_server(line):
    if not("@" in line):
        raise Exception("Receiver email is not valid")
    temp = line.split("@", 1)[1]
    return temp.split(">", 1)[0]


def sendMail(file):
    f = open(file, "r")
    file_contents = f.read()
    upper_parts = file_contents.split('\n', 3)
    from_line = upper_parts[0]
    from_email = "<"+from_line.split(" <", 1)[1]
    to_line = upper_parts[1]
    to_email = "<"+to_line.split(" <", 1)[1]
    subject_line = upper_parts[2]
    email_con = file_contents.split("\n\n", 1)[1]
    # Specify the mail server and port number
    # Need to lookup recipient email server not sender
    systemRead = popen("nslookup -q=MX " + get_smtp_server(to_line))
    port = 25

    mailserver = systemRead.read().split("mail exchanger = ", 1)[1]
    systemRead.close()
    mailserver = mailserver.split("\n", 1)[0]
    # Create a socket and connect to the mail server
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((mailserver, port))

    # Receive the connection greeting message from the server
    recv = clientSocket.recv(1024)
    if not (b"220" in recv):
        print("Failure")
        raise Exception("Could not connect to mail server successfully")

    clientSocket.send(b'HELO Server\r\n')
    recv = clientSocket.recv(1024)
    if not check250(recv):
        raise Exception("Could not say hello properly")

    # Send the MAIL FROM command and receive the server response
    mailFromCommand = 'MAIL FROM: '+from_email+'\r\n'
    clientSocket.send(mailFromCommand.encode())
    recv = clientSocket.recv(1024)
    if not check250(recv):
        raise Exception("Mail from user to accepted")

    # Send the RCPT TO command and receive the server response
    rcptToCommand = 'RCPT TO: '+to_email+'\r\n'
    clientSocket.send(rcptToCommand.encode())
    recv = clientSocket.recv(1024)
    if not check250(recv):
        print(recv)
        raise Exception("Mail to user is not possible")

    # Send the DATA command and receive the server response
    dataCommand = 'DATA\r\n'
    clientSocket.send(dataCommand.encode())
    recv = clientSocket.recv(1024)

    # Send the email message
    message = from_line+"\r\n"
    message += to_line+'\r\n'
    message += subject_line+'\r\n'
    message += '\r\n'
    message += email_con+'\r\n'
    message += '.\r\n'
    clientSocket.send(message.encode())
    recv = clientSocket.recv(1024)
    if not check250(recv):
        raise Exception("Could not send mail")
    # Send the QUIT command and receive the server response
    quitCommand = 'QUIT\r\n'
    clientSocket.send(quitCommand.encode())
    recv = clientSocket.recv(1024)
    if not (b"221" in recv):
        print("Failure")
        raise Exception("Could not close connection to mail server")
    clientSocket.close()


def main():
    args = sys.argv
    if len(args) == 1:
        return
    args.pop(0)
    for each in args:
        sendMail(each)


if __name__ == "__main__":
    main()
