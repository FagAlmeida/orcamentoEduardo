from flask import Flask, redirect, render_template, request, url_for
from flask_pymongo import PyMongo

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

app.config["MONGO_URI"] = "mongodb+srv://fagalmeida:1234@cluster0.xm9sz.mongodb.net/meu_banco?retryWrites=true&w=majority"

mongo = PyMongo(app)

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
