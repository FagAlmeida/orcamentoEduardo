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

        if nome and endereco and email and whatsapp:  # Verifica se todos os campos foram preenchidos
            return redirect(url_for('dimensoes'))  # Redireciona para a página "dimensoes.html"
        else:
            erro = "Preencha todos os campos corretamente!"
            return render_template('infop.html', erro=erro)  # Reexibe o formulário com erro

    return render_template('infop.html')  # Exibe o formulário caso seja uma requisição GET



@app.route('/trabalhos')
def trabalhos():
    return render_template('trabalhos.html')

@app.route('/dimensoes')
def dimensoes():
    return render_template('dimensoes.html')

if __name__ == '__main__':
    app.run(debug=True)

