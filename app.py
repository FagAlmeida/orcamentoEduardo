from flask import Flask, redirect, render_template, request, url_for, session
from flask_pymongo import PyMongo
import urllib.parse

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

# Configuração do MongoDB
app.config["MONGO_URI"] = "mongodb+srv://fagalmeida:1234@cluster0.xm9sz.mongodb.net/meu_banco?retryWrites=true&w=majority"
mongo = PyMongo(app)

usuarios_collection = mongo.db.usuarios

@app.route('/', methods=['GET'])
def inicial():
    return render_template('inicial.html')

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
            session['telefone'] = telefone
            return redirect(url_for('infop'))
        else:
            erro = "Usuário não encontrado ou dados incorretos!"
            return render_template('login.html', erro=erro)

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form.get("nome")
        telefone = request.form.get("telefone")
        email = request.form.get("email")

        if not nome or not telefone or not email:
            erro = "Preencha todos os campos!"
            return render_template('register.html', erro=erro)

        usuario_existente = usuarios_collection.find_one({"$or": [{"telefone": telefone}, {"email": email}]})
        if usuario_existente:
            erro = "Usuário já registrado!"
            return render_template('register.html', erro=erro)

        # Cria o perfil do usuário
        usuarios_collection.insert_one({"nome": nome, "telefone": telefone, "email": email})
        session['telefone'] = telefone
        return redirect(url_for('infop'))

    return render_template('register.html')

@app.route('/infop', methods=['GET', 'POST'])
def infop():
    if 'telefone' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        endereco = request.form.get('endereco')
        numero = request.form.get('numero')
        cidade = request.form.get('cidade')
        cep = request.form.get('cep')
        tipo = request.form.get('tipo')
        telefone = session['telefone']

        # Atualiza os dados do usuário com as informações do infop
        usuarios_collection.update_one(
            {"telefone": telefone},
            {"$set": {
                "endereco": endereco,
                "numero": numero,
                "cidade": cidade,
                "cep": cep,
                "tipo": tipo
            }}
        )

        # Redireciona para a página escolhida
        if tipo == 'box':
            return redirect(url_for('box'))
        elif tipo == 'espelho':
            return redirect(url_for('espelho'))
        elif tipo == 'porta':
            return redirect(url_for('porta'))
        
    return render_template('infop.html')



@app.route('/box', methods=['GET', 'POST'])
def box():
    if 'telefone' not in session:
        return redirect(url_for('login'))

    telefone = session['telefone']
    usuario = usuarios_collection.find_one({"telefone": telefone})

    if request.method == 'POST':
        modelo = request.form.get('modelo')
        tipo = request.form.get('tipo')
        largura = request.form.get('largura')
        vidro = request.form.get('vidro')

        # Atualiza os dados do usuário com as informações do box
        usuarios_collection.update_one(
            {"telefone": telefone},
            {"$set": {
                "box": {
                    "modelo": modelo,
                    "tipo": tipo,
                    "largura": largura,
                    "vidro": vidro
                }
            }}
        )

        # Monta a mensagem para o WhatsApp
        mensagem = f"""
        *Confirmação do Pedido - Box*
        📛 *Nome:* {usuario['nome']}
        📱 *Telefone:* {usuario['telefone']}
        📧 *Email:* {usuario['email']}
        🏠 *Endereço:* {usuario.get('endereco', 'Não informado')}, {usuario.get('numero', 'Não informado')}
        🏙️ *Cidade:* {usuario.get('cidade', 'Não informado')}
        📮 *CEP:* {usuario.get('cep', 'Não informado')}
        🚪 *Tipo de Produto:* {usuario.get('tipo', 'Não informado')}
        
        📦 *Box:*
        - *Modelo:* {modelo}
        - *Tipo:* {tipo}
        - *Largura:* {largura}
        - *Vidro:* {vidro}
        
        Confirma seu pedido? Entre em contato para finalizar!
        """

        # Codifica a mensagem para URL
        mensagem_encoded = urllib.parse.quote(mensagem.strip())
        meu_numero = "+553598404619"  # Substitua pelo seu número com DDI e DDD
        whatsapp_url = f"https://wa.me/{meu_numero}?text={mensagem_encoded}"
        
        # Redireciona para o WhatsApp
        return redirect(whatsapp_url)
    
    return render_template('box.html', usuario=usuario)

    
@app.route('/espelho', methods=['GET', 'POST'])
def espelho():
    if 'telefone' not in session:
        return redirect(url_for('login'))

    telefone = session['telefone']
    usuario = usuarios_collection.find_one({"telefone": telefone})

    if request.method == 'POST':
        modelo = request.form.get('modelo')
        tipo = request.form.get('tipo')
        largura = request.form.get('largura')
        vidro = request.form.get('vidro')

        # Atualiza os dados do usuário com as informações do espelho
        usuarios_collection.update_one(
            {"telefone": telefone},
            {"$set": {
                "espelho": {
                    "modelo": modelo,
                    "tipo": tipo,
                    "largura": largura,
                    "vidro": vidro
                }
            }}
        )

        # Monta a mensagem para o WhatsApp
        mensagem = f"""
        *Confirmação do Pedido - Espelho*
        📛 *Nome:* {usuario['nome']}
        📱 *Telefone:* {usuario['telefone']}
        📧 *Email:* {usuario['email']}
        🏠 *Endereço:* {usuario.get('endereco', 'Não informado')}, {usuario.get('numero', 'Não informado')}
        🏙️ *Cidade:* {usuario.get('cidade', 'Não informado')}
        📮 *CEP:* {usuario.get('cep', 'Não informado')}
        🚪 *Tipo de Produto:* {usuario.get('tipo', 'Não informado')}
        
        🪞 *Espelho:*
        - *Modelo:* {modelo}
        - *Tipo:* {tipo}
        - *Largura:* {largura}
        - *Vidro:* {vidro}
        
        Confirma seu pedido? Entre em contato para finalizar!
        """

        # Codifica a mensagem para URL
        mensagem_encoded = urllib.parse.quote(mensagem.strip())
        meu_numero = "+553598404619"  # Substitua pelo seu número com DDI e DDD
        whatsapp_url = f"https://wa.me/{meu_numero}?text={mensagem_encoded}"
        
        # Redireciona para o WhatsApp
        return redirect(whatsapp_url)
    
    return render_template('espelho.html', usuario=usuario)

@app.route('/porta', methods=['GET', 'POST'])
def porta():
    if 'telefone' not in session:
        return redirect(url_for('login'))  # Redireciona para login caso não tenha telefone na sessão

    telefone = session['telefone']
    usuario = usuarios_collection.find_one({"telefone": telefone})

    return render_template('porta.html', usuario=usuario)

@app.route('/trabalhos')
def trabalhos():
    return render_template('trabalhos.html')

@app.route('/logout')
def logout():
    session.pop('telefone', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
