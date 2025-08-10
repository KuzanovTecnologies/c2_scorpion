# app_vulneravel.py
from flask import Flask, request, send_from_directory
import os
import pickle

app = Flask(__name__)
app.config['DEBUG'] = True                      # <-- perigoso em produção
app.config['SECRET_KEY'] = 'super-secret-key'   # <-- não colocar hardcoded

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return "Hello insecure app!"

# insecure file upload: no validation, saves original filename
@app.route('/upload', methods=['POST'])
def upload():
    f = request.files['file']
    f.save(os.path.join(UPLOAD_FOLDER, f.filename))
    return "Uploaded"

# insecure endpoint that uses pickle on user input (DANGEROUS)
@app.route('/load', methods=['POST'])
def load():
    data = request.data
    obj = pickle.loads(data)   # <-- unsafe: deserializing untrusted data
    return f"Loaded object type: {type(obj)}"

# serving files directly; if uploads allow .py could leak source or be executed elsewhere
@app.route('/files/<path:filename>')
def files(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)
