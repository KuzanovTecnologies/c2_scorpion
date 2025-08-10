# insecure_design.py

class Usuario:
    def __init__(self, username, role="user"):
        self.username = username
        self.role = role

    def __str__(self):
        return f"Usuário: {self.username} | Permissão: {self.role}"

def alterar_perfil(usuario, dados):
    """
    Função que permite alterar dados do perfil sem validação.
    Exemplo de design inseguro.
    """
    for chave, valor in dados.items():
        setattr(usuario, chave, valor)  # altera qualquer atributo direto, sem validação

if __name__ == "__main__":
    user = Usuario("joao")

    print("Antes da alteração:")
    print(user)

    # Dados enviados pelo usuário para alteração (simulando entrada não confiável)
    dados_recebidos = {
        "role": "admin",  # alteração insegura que deveria ser proibida
        "username": "joao_123"
    }

    alterar_perfil(user, dados_recebidos)

    print("\nDepois da alteração:")
    print(user)
