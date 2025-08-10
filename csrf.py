from flask import Flask, request, session, abort
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

@app.before_request
def csrf_protect():
    if request.method in ("POST", "PUT", "DELETE"):
        token = session.get("_csrf_token", None)
        request_token = request.form.get("_csrf_token") or request.headers.get("X-CSRF-Token")
        
        if not token or not request_token or token != request_token:
            abort(403)  # Bloqueia CSRF

def generate_csrf_token():
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_hex(32)
    return session["_csrf_token"]

app.jinja_env.globals["csrf_token"] = generate_csrf_token

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        return "Requisição POST aceita com token válido!"
    return f"""
        <form method="POST">
            <input type="hidden" name="_csrf_token" value="{generate_csrf_token()}">
            <input type="submit" value="Enviar POST">
        </form>
    """

if __name__ == "__main__":
    app.run(debug=True)
