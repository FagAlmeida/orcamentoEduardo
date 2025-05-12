from flask import Flask, redirect, render_template, request, url_for, session
from flask_pymongo import PyMongo
import re

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

# Configuração do MongoDB
app.config["MONGO_URI"] = "mongodb+srv://fagalmeida:1234@cluster0.xm9sz.mongodb.net/meu_banco?retryWrites=true&w=majority"

mongo = PyMongo(app)

# Definir a coleção de usuários
usuarios_collection = mongo.db.usuarios

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        telefone = request.form.get('telefone').strip()
        usuario = usuarios_collection.find_one({'telefone': telefone})

        if usuario:
            return redirect(url_for('infop'))
        else:
            erro = "Usuário não encontrado ou dados incorretos!"
            return render_template('login.html', erro=erro)

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form.get("nome").strip()
        telefone = request.form.get("telefone").strip()
        email = request.form.get("email").strip().lower()
        username = request.form.get("username") or nome.lower().replace(" ", "_")

        # Validação do email
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            erro = "Formato de email inválido!"
            return render_template('register.html', erro=erro)

        if nome and telefone and email:
            usuario_existente = usuarios_collection.find_one({"$or": [{"telefone": telefone}, {"username": username}, {"email": email}]})
            if usuario_existente:
                erro = "Usuário, telefone ou email já registrado."
                return render_template('register.html', erro=erro)

            usuarios_collection.insert_one({"nome": nome, "telefone": telefone, "username": username, "email": email})
            session['telefone'] = telefone
            return redirect(url_for('login'))
        else:
            erro = "Preencha todos os campos!"
            return render_template('register.html', erro=erro)
    return render_template('register.html')

@app.route('/')
def inicial():
    return render_template('inicial.html')

@app.route('/infop', methods=['GET', 'POST'])
def infop():
    if request.method == 'POST':
        nome = request.form.get("username")
        endereco = request.form.get("address")
        email = request.form.get("email")
        whatsapp = request.form.get("whatsapp")
        tipo = request.form.get("tipo")

        if nome and endereco and email and whatsapp and tipo:
            if tipo == "box":
                return redirect(url_for('box'))
            elif tipo == "espelho":
                return redirect(url_for('espelho'))
            elif tipo == "porta":
                return redirect(url_for('porta'))
            else:
                erro = "Tipo inválido selecionado."
                return render_template('infop.html', erro=erro)
        else:
            erro = "Preencha todos os campos corretamente!"
            return render_template('infop.html', erro=erro)

    return render_template('infop.html')

@app.route('/trabalhos')
def trabalhos():
    return render_template('trabalhos.html')

@app.route('/box')
def box():
    return render_template('box.html')

@app.route('/espelho')
def espelho():
    return render_template('espelho.html')

@app.route('/porta')
def porta():
    return render_template('porta.html')

if __name__ == '__main__':
    app.run(debug=True)
