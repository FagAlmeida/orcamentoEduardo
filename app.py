from flask import Flask, redirect, render_template, request, url_for, session
from flask_pymongo import PyMongo

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
        telefone = request.form.get('telefone').strip()  # Garantir que não haja espaços extras
        usuario = usuarios_collection.find_one({'telefone': telefone})

        if usuario:
            return redirect(url_for('infop'))  # Redireciona para a página infop.html
        else:
            erro = "Usuário não encontrado ou dados incorretos!"
            return render_template('login.html', erro=erro)

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form.get("nome")
        telefone = request.form.get("telefone")
        username = request.form.get("username")  # Supondo que 'username' seja um campo do formulário

        if not username:
            # Se o username não for informado, você pode gerar um automaticamente
            username = nome.lower().replace(" ", "_")  # Exemplo de geração de username simples

        if nome and telefone:
            # Verifica se já existe um usuário com o mesmo telefone ou username
            usuario_existente = mongo.db.usuarios.find_one({"$or": [{"telefone": telefone}, {"username": username}]})
            if usuario_existente:
                erro = "Usuário ou telefone já registrado."
                return render_template('login.html', erro=erro)

            # Registra o novo usuário no MongoDB
            mongo.db.usuarios.insert_one({"nome": nome, "telefone": telefone, "username": username})
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
        tipo = request.form.get("tipo")  # Captura o valor do select

        if nome and endereco and email and whatsapp and tipo:
            # Aqui você pode salvar os dados no MongoDB se quiser
            # mongo.db.usuarios.insert_one({ ... })

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
