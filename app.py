from flask import Flask, redirect, render_template, request, url_for, session
from flask_pymongo import PyMongo
import urllib.parse
import os
from bson.objectid import ObjectId


app = Flask(__name__)

# IMPORTANTE: Nunca deixe a chave secreta hardcoded em produção!
# Use variável de ambiente para definir a chave secreta segura
app.secret_key = os.environ.get('SECRET_KEY', 'uma_chave_muito_forte_e_aleatoria')

# Configuração do MongoDB - use variável de ambiente para segurança
app.config["MONGO_URI"] = os.environ.get(
    "MONGO_URI",
    "mongodb+srv://fagalmeida:1234@cluster0.xm9sz.mongodb.net/meu_banco?retryWrites=true&w=majority"
)

mongo = PyMongo(app)
usuarios_collection = mongo.db.usuarios

# CONFIGURAÇÕES DE SEGURANÇA DOS COOKIES DE SESSÃO
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,   # Protege contra acesso via JavaScript (XSS)
    SESSION_COOKIE_SECURE=True,     # Envia cookie só via HTTPS (deixe False se não usar HTTPS localmente)
    SESSION_COOKIE_SAMESITE='Lax'   # Protege contra CSRF parcialmente
)

# CABEÇALHOS DE SEGURANÇA HTTP
@app.after_request
def aplicar_cabecalhos_de_seguranca(response):
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "style-src 'self' 'unsafe-inline' https:; "
        "script-src 'self' 'unsafe-inline' https:; "
        "img-src 'self' data: https:; "
        "font-src 'self' https: data:; "
        "object-src 'none'; "
        "frame-ancestors 'none'; "
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"  # HSTS para HTTPS
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=()"               # Exemplo de política de permissões
    return response

# FORÇA REDIRECIONAMENTO HTTP -> HTTPS (use só se HTTPS estiver ativo no servidor)
@app.before_request
def redirecionar_para_https():
    # Se não estiver usando HTTPS, comente ou remova essa função para não bloquear localmente
    if not request.is_secure and not app.debug:
        url = request.url.replace("http://", "https://", 1)
        return redirect(url, code=301)

@app.route('/', methods=['GET'])
def inicial():
    return render_template('inicial.html')

@app.route('/solicitar', methods=['POST'])
def solicitar():
    # Aqui você já deve ter os campos do formulário
    nome = request.form.get("nome")
    telefone = request.form.get("telefone")
    tipo = request.form.get("tipo")
    modelo = request.form.get("modelo")
    largura = request.form.get("largura")
    vidro = request.form.get("vidro")
    cpf = request.form.get("cpf")
    endereco = request.form.get("endereco")
    numero = request.form.get("numero")
    cidade = request.form.get("cidade")
    cep = request.form.get("cep")

    # Monta documento
    usuario = {
        "nome": nome,
        "cpf": cpf,
        "endereco": endereco,
        "numero": numero,
        "cidade": cidade,
        "cep": cep,
        "telefone": telefone,
        "tipo": tipo,
        "espelho": {
            "modelo": modelo,
            "tipo": "Espelho" if tipo == "espelho" else "",
            "largura": largura,
            "vidro": vidro
        }
    }

    # Salva no banco
    usuarios_collection.insert_one(usuario)

    # Redireciona para WhatsApp
    whatsapp_url = f"https://wa.me/55{telefone}?text=Olá%20{nome},%20sua%20solicitação%20de%20{tipo}%20foi%20recebida."
    return redirect(whatsapp_url)

@app.route('/admin')
def admin():
    usuarios = list(usuarios_collection.find().sort("_id", -1))
    return render_template("admin.html", usuarios=usuarios)

@app.route('/admin/<id>')
def admin_detalhes(id):
    usuario = usuarios_collection.find_one({"_id": ObjectId(id)})
    return render_template("detalhes.html", usuario=usuario)

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

@app.route('/termos.html')
def termos():
    return render_template('termos.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    erro = None
    if request.method == 'POST':
        nome = request.form.get('nome')
        cpf = request.form.get('cpf')
        endereco = request.form.get('endereco')
        numero = request.form.get('numero')
        cidade = request.form.get('cidade')
        cep = request.form.get('cep')
        telefone = request.form.get('telefone')

        if not (nome and cpf and endereco and numero and cidade and cep and telefone):
            erro = "Por favor, preencha todos os campos."
        else:
            if usuarios_collection.find_one({"telefone": telefone}):
                erro = "Telefone já cadastrado."
            else:
                usuarios_collection.insert_one({
                    "nome": nome,
                    "cpf": cpf,
                    "endereco": endereco,
                    "numero": numero,
                    "cidade": cidade,
                    "cep": cep,
                    "telefone": telefone,
                    "tipo": "box"
                })
                return redirect(url_for('login'))

    return render_template('register.html', erro=erro)

@app.route('/infop', methods=['GET', 'POST'])
def infop():
    if 'telefone' not in session:
        return redirect(url_for('login'))

    telefone = session['telefone']

    if request.method == 'POST':
        campos_para_atualizar = {}
        for campo in ['endereco', 'numero', 'cidade', 'cep', 'tipo']:
            valor = request.form.get(campo)
            if valor:
                campos_para_atualizar[campo] = valor

        if campos_para_atualizar:
            usuarios_collection.update_one(
                {"telefone": telefone},
                {"$set": campos_para_atualizar}
            )

        tipo = request.form.get('tipo')
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

    if request.method == 'POST':
        modelo = request.form.get('modelo')
        tipo = request.form.get('tipo')
        largura = request.form.get('largura')
        vidro = request.form.get('vidro')

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

        usuario = usuarios_collection.find_one({"telefone": telefone})

        def valor_ou_nao_informado(d, campo):
            v = d.get(campo)
            return 'Não informado' if v in (None, '', 'null') else v

        endereco = valor_ou_nao_informado(usuario, 'endereco')
        numero = valor_ou_nao_informado(usuario, 'numero')
        cidade = valor_ou_nao_informado(usuario, 'cidade')
        cep = valor_ou_nao_informado(usuario, 'cep')
        email = valor_ou_nao_informado(usuario, 'email')
        tipo_produto = valor_ou_nao_informado(usuario, 'tipo')

        mensagem = f"""*Confirmação do Pedido - Box*
📛 *Nome:* {valor_ou_nao_informado(usuario, 'nome')}
📱 *Telefone:* {valor_ou_nao_informado(usuario, 'telefone')}
📧 *Email:* {email}
🏠 *Endereço:* {endereco}, {numero}
🏙️ *Cidade:* {cidade}
📮 *CEP:* {cep}
🚪 *Tipo de Produto:* {tipo_produto}

📦 *Box:*
- *Modelo:* {modelo}
- *Tipo:* {tipo}
- *Largura:* {largura}
- *Vidro:* {vidro}

Confirma seu pedido? Entre em contato para finalizar!
"""

        mensagem_encoded = urllib.parse.quote(mensagem.strip())
        meu_numero = "+5535999999999"
        whatsapp_url = f"https://wa.me/{meu_numero}?text={mensagem_encoded}"

        return redirect(whatsapp_url)

    usuario = usuarios_collection.find_one({"telefone": telefone})
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

        mensagem = f"""
        *Confirmação do Pedido - Espelho*
        📛 *Nome:* {usuario['nome']}
        📱 *Telefone:* {usuario['telefone']}
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

        mensagem_encoded = urllib.parse.quote(mensagem.strip())
        meu_numero = "+553598404619"
        whatsapp_url = f"https://wa.me/{meu_numero}?text={mensagem_encoded}"
        
        return redirect(whatsapp_url)
    
    return render_template('espelho.html', usuario=usuario)

@app.route('/porta', methods=['GET', 'POST'])
def porta():
    if 'telefone' not in session:
        return redirect(url_for('login'))

    telefone = session['telefone']
    usuario = usuarios_collection.find_one({"telefone": telefone})

    if request.method == 'POST':
        modelo = request.form.get('modelo')
        tipo = request.form.get('tipo')
        largura = request.form.get('largura')
        vidro = request.form.get('vidro')

        usuarios_collection.update_one(
            {"telefone": telefone},
            {"$set": {
                "modelo": modelo,
                "tipo": tipo,
                "largura": largura,
                "vidro": vidro
            }}
        )

        mensagem = f"""*Confirmação do Pedido - Porta*\n
📛 *Nome:* {usuario.get('nome')}\n
📱 *Telefone:* {usuario.get('telefone')}\n
📧 *Email:* {usuario.get('email')}\n
🏠 *Endereço:* {usuario.get('endereco', 'Não informado')}\n
🏙️ *Cidade:* {usuario.get('cidade', 'Não informado')}\n
📮 *CEP:* {usuario.get('cep', 'Não informado')}\n\n
🚪 *Tipo de Produto:* {tipo}\n
📦 *Porta:*\n
- *Modelo:* {modelo}\n
- *Largura:* {largura}\n
- *Vidro:* {vidro}\n
Confirma seu pedido? Entre em contato para finalizar!"""

        numero_whatsapp = '553598404619'
        link = f"https://wa.me/{numero_whatsapp}?text={urllib.parse.quote(mensagem)}"
        return redirect(link)

    return render_template('porta.html', usuario=usuario)

@app.route('/trabalhos')
def trabalhos():
    return render_template('trabalhos.html')

@app.route('/logout')
def logout():
    session.pop('telefone', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Em produção, use um servidor como gunicorn e HTTPS configurado no servidor
    app.run(debug=True)
