import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/fetch')
def fetch_url():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL é obrigatória'}), 400

    try:
        # Faz a requisição para a URL fornecida
        response = requests.get(url, timeout=5)
        return jsonify({
            'url': url,
            'status_code': response.status_code,
            'content': response.text[:500]  # retorna só os primeiros 500 caracteres para evitar resposta gigante
        })
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
