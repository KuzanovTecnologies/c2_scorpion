# rce.py - exemplo de vulnerabilidade RCE para aprendizado

import os

def vulnerable():
    cmd = input("Digite um comando para executar no sistema: ")
    # ATENÇÃO: Não faça isso em produção!
    os.system(cmd)

if __name__ == "__main__":
    print("Exemplo vulnerável de execução remota de código.")
    vulnerable()
