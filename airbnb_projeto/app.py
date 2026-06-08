from flask import Flask, redirect
from admin import admin_bp
from anfitriao import anfitriao_bp
from hospede import hospede_bp

app = Flask(__name__)

# Registra os módulos (Blueprints)
app.register_blueprint(admin_bp)
app.register_blueprint(anfitriao_bp)
app.register_blueprint(hospede_bp)

# Rota raiz redireciona para a visão do Hóspede por padrão
@app.route('/')
def index():
    return redirect('/hospede/')

if __name__ == '__main__':
    app.run(debug=True, port=5000)