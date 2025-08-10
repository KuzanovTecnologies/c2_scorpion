# app_seguro.py
from flask import Flask, request, send_from_directory, abort
import os
import werkzeug.utils
from itsdangerous import URLSafeSerializer

app = Flask(__name__)
app.config['DEBUG'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')  # carregar de env / secret manager

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png','jpg','jpeg','gif','txt','pdf'}

def allowed_filename(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        abort(400)
    f = request.files['file']
    filename = werkzeug.utils.secure_filename(f.filename)  # sanitize
    if not allowed_filename(filename):
        abort(400)
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    f.save(save_path)
    return "Uploaded"

# remove qualquer uso de pickle para dados não confiáveis
# se precisar serializar, usar JSON ou itsdangerous/cryptography com validação
@app.route('/load-json', methods=['POST'])
def load_json():
    # exemplo seguro: aceitar apenas JSON e validar esquema
    data = request.get_json()
    if not isinstance(data, dict):
        abort(400)
    # validar campos esperados aqui...
    return "OK"

# servir arquivos apenas se necessário e com headers apropriados
@app.route('/files/<path:filename>')
def files(filename):
    filename = werkzeug.utils.secure_filename(filename)
    if not allowed_filename(filename):
        abort(404)
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
