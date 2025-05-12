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
enderecos_collection = mongo.db.enderecos  # Coleção de endereços

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        telefone = request.form.get('telefone')
        if telefone:
            telefone = telefone.strip()
        else:
            erro = "Telefone não pode ser vazio!"
            return render_template('login.html', erro=erro)
        
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
        nome = request.form.get("nome")
        if nome:
            nome = nome.strip()
        else:
            erro = "Nome não pode ser vazio!"
            return render_template('register.html', erro=erro)

        telefone = request.form.get("telefone")
        if telefone:
            telefone = telefone.strip()
        else:
            erro = "Telefone não pode ser vazio!"
            return render_template('register.html', erro=erro)

        email = request.form.get("email")
        if email:
            email = email.strip().lower()
        else:
            erro = "Email não pode ser vazio!"
            return render_template('register.html', erro=erro)

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
        # Coleta as informações do formulário
        endereco = request.form['endereco']
        numero = request.form['numero']
        cidade = request.form['cidade']
        cep = request.form['cep']
        tipo = request.form['tipo']  # Captura a opção escolhida
        
        # Salva as informações no MongoDB
        data = {
            'endereco': endereco,
            'numero': numero,
            'cidade': cidade,
            'cep': cep,
            'tipo': tipo
        }
        enderecos_collection.insert_one(data)  # Insere na coleção de endereços
        
        # Redireciona para a página escolhida
        if tipo == 'box':
            return redirect(url_for('box'))
        elif tipo == 'espelho':
            return redirect(url_for('espelho'))
        elif tipo == 'porta':
            return redirect(url_for('porta'))
        
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
