# Importando o Flask e as libs necessárias
from flask import Flask, render_template, session, request, redirect
# Importando os
import os, time
# Importando as funcões, classes e objetos
import funcoes

# lib time posteriormente para prevenir imagens com nome duplicados
from werkzeug.security import check_password_hash, generate_password_hash

# Próximo passo:

# Imagens (https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/) (https://www.youtube.com/watch?v=WAizZ3zYFBM)
# Rota adicionar
# Home com imagens

# Proteção contra usuario não logados
# Evitar erros e prevenção de bugs

# Criando app, secret key, e configurações do app

app = Flask(__name__)
app.secret_key = "abcdefg"
caminho_atual = os.getcwd()
UPLOAD_FOLDER = caminho_atual + "/MeuSite/static/images/upload"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Try except mais robusto posteriormete
# ALLOWED PERMISSION PARA IMAGEM

# Rota Home
@app.route("/")
def home():
    try:
        if "login" not in session:
            session["login"] = False
        
        catalogo = funcoes.mostrarProdutos()
        return render_template("index.html", catalogo=catalogo)
    
    except Exception as error:
        mensagem = error
        return render_template("mensagem.html", mensagem=mensagem)

# Redireciona para a página de registro de usuários
@app.route("/registrar")
def rotaRegistrar():
    try:
        return render_template("registrar.html")
    except Exception as error:
        mensagem = error
        return render_template("mensagem.html", mensagem=mensagem)

# Recebe os dados do formulário da página de registro, cria o usuário e adiciona este no catálogo
@app.route("/efetuarRegistrar", methods=["GET", "POST"])
def efetuarRegistrar():
    try:
        if request.method == "POST":
            nome = request.form["nome"]
            email = request.form["email"]
            senha = request.form["senha"] 
            hash_senha = generate_password_hash(str(senha))
            rota = funcoes.registro_usuario(nome, email, hash_senha)
            return rota
    except Exception as error:
        mensagem = error
        return render_template("mensagem.html", mensagem=mensagem)

# Redireciona para a página de login
@app.route("/login")
def rotaLogin():
    try:
        return render_template("login.html")
    except Exception as error:
        mensagem = error
        return render_template("mensagem.html", mensagem=mensagem)

# Recebe os dados do formulário da página de login e verifica o email e senha para cada usuario cadastrado no catalogo
@app.route("/efetuarLogin", methods=["GET","POST"])
def efetuarLogin():
    try:
        if request.method == "POST":
            email = request.form["email"]
            senha = request.form["senha"]
            rota = funcoes.login_usuario(email, senha)
            return rota
    except Exception as error:
        mensagem = error
        return render_template("mensagem.html", mensagem=mensagem)

# Logout da sessão e retorno para Home
@app.route("/logout")
def logout():
    try:
        if session["login"] == True:
            session["login"] = False
        return redirect("/")
    except Exception as error:
        mensagem = error
        return render_template("mensagem.html", mensagem=mensagem)

# # Redireciona para a página de adicionar novos produtos
@app.route("/adicionar")
def rotaAdicionar():
    try:
        return render_template("adicionar_produto.html")
    except Exception as error:
        mensagem = error
        return render_template("mensagem.html", mensagem=mensagem)

# Recebe os dados para adicionar um novo produto e salva a imagem no computador

@app.route("/efetuarAdicionar", methods=["GET", "POST"])
def efetuarAdicionar():
    try:
        if request.method == "POST" and session["login"] == True:
            #dados para adicionar determinado produto
            #form e inputs + html
            titulo = request.form["titulo"]
            descricao = request.form["descricao"]
            valor = request.form["valor"]
            # Caso o usuário não enviou a foto
            imagem = request.files["imagem"]
            nomeImagem = imagem.filename
            # Necessário = titulo, descricao, valor (decimal), upload_imagem, nomeImagem, id_usuario_produto
            funcoes.adicionarProduto(titulo, descricao, valor, nomeImagem, session["user_id"])
            funcoes.upload_imagem(UPLOAD_FOLDER, imagem, nomeImagem)
            return redirect("/")
        
    except Exception as error:
        mensagem = error
        return render_template("mensagem.html", mensagem=mensagem)

@app.route("/perfil/<user_id>")
def user_perfil(user_id):
    try:
        usuario = funcoes.procurar_usuario_id(user_id)
        return render_template("user_perfil.html", usuario_nome=usuario["nome"], usuario_email=usuario["email"], produtos_usuario=usuario["user_products"])
    except Exception as error:
        mensagem = error
        return render_template("mensagem.html", mensagem=mensagem)

# Nova rota para visualizar produto

@app.route("/produto/<produto_id>")
def visualizar_produto(produto_id):
    try:
        produto = funcoes.procurar_produto_id(produto_id)
        usuario = funcoes.procurar_usuario_id(produto["id_usuario_produto"])
        return render_template("visualizar_produto.html", produto=produto, nome_usuario=usuario["nome"])
    except Exception as error:
        mensagem = error
        return render_template("mensagem.html", mensagem=mensagem)

# Rodar o app
if __name__ == "__main__":
    app.run(debug=True)
