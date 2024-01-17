from flask import Flask, render_template, redirect, session
import os, psycopg2
from werkzeug.security import check_password_hash, generate_password_hash
from config import config

class Conexao:
    def __init__(self):
        params = config()
        self.conexao = psycopg2.connect(**params)
        
    def cursor(self):
        return self.conexao.cursor()

    def commit(self):
        self.conexao.commit()

    def close(self):
        self.conexao.close()

connect = Conexao()
cursor = connect.cursor()

# Testes

# Quicksort posteriormente
def ordenando(lista):
    return lista.sort()

def binary_search_sql(listaBusca, itemRequerido):
    baixo = 0 # Iniciamos a contagem em 0
    alto = len(listaBusca) - 1 # Fim da lista (lista começa em 0, 1, 2...)
    while baixo <= alto: # Algoritmo para no momento em que a média se tornar negativa. Baixo fica com valor maior que o alto. Baixo = meio + 1 maior que o alto. Isso acontece a partir que chegamos no fim da lista e a varíavel baixo incrementa o meio + 1.
        meio = int((baixo + alto) / 2) # Média aritmética da lista (menor e maior número). Convertemos para inteiro.
        chute = listaBusca[meio] # Chute vai ser feito na metade da lista (Busca binária)
        # Lista retornada é uma tupla nesse caso, precisamos acessar o índice [1]
        if chute[1] == itemRequerido: # Se acertar, o algoritmo retorna True
            # Retornamos True, apenas para check
            return {"resultado":True,
                    "id_usuario":chute[0]}
        if chute[1] > itemRequerido: # Se o chute for maior que o item requerido a lista é reduzida pela metade - 1
            alto = meio - 1 
        if chute[1] < itemRequerido: # Se o chute for menor que o item requerido a lista agora começa pelo meio + 1
            baixo = meio + 1
    
    return {"resultado":None}

def checarEmail(email):
    # Seleciona o campo email de todas as instâncias
    sql = """select id, email from usuario order by email"""
    # Executa o sql
    cursor.execute(sql)
    # Resultado = lista com tuplas contendo cada sentença do banco de dados
    resultado = cursor.fetchall()
    # "Salva" as execuções sql
    connect.commit()
    # Se tiver algo na lista de instâncias
    if len(resultado) > 0:
        # Possivel implementação de pesquisa binária e quicksort posteriormente
        resultado = binary_search_sql(resultado, email)
    return resultado

def checarSenha(hash_senha, senha):
    return check_password_hash(hash_senha, senha)

def procurar_usuario_id(user_id):
    # Seleciona todas as informações do usuario que possui o id fornecido
    sql = f"""select * from usuario where id = {user_id}"""
    cursor.execute(sql)
    # Resultado vira uma tupla
    info_usuario = cursor.fetchone()
    connect.commit()
    produtos_usuario = procurar_produtos_usuario(user_id)
    # Todas as informações são passadas para um dicionário com o intuito de facilitar
    usuario = {"id":info_usuario[0],
               "nome":info_usuario[1],
               "email":info_usuario[2],
               "senha_hash":info_usuario[3],
               "user_products":produtos_usuario}
    # Retornamos a variável que contém o dicionário
    return usuario

def mostrarProdutos():
    # Query sql retornando uma lista com todas os produtos
    # Se tiver produtos retorna a lista se não tiver retorna None

    sql = """select * from produto"""
    cursor.execute(sql)
    resultado = cursor.fetchall()
    connect.commit()
    if len(resultado) > 0:
        return resultado
    else:
        return None
    
def registro_usuario(nome, email, senha):
    # Checa se o email já foi vinculado
    # Retorno True para email vinculado; False para email não vinculado; None para nenhum elemento no banco de dados
    checkEmail = checarEmail(email)
    # Email já cadastrado, retorna uma mensagem informando email cadastrado
    if checkEmail["resultado"] == True:
        mensagem = "Esse e-mail já foi cadastrado anteriormente em nosso sistema"
        rota = render_template("mensagem.html", mensagem=mensagem)

    # Email não cadastrado.
    if checkEmail["resultado"] == None:
        # Inserindo na tabela usuario nome, email e senha_hash
        sql = f"""insert into usuario (nome, email, senha) values ('{nome}', '{email}', '{senha}')"""
        cursor.execute(sql)
        connect.commit()
        # Mensagem informando cadastro do email
        mensagem = "E-mail cadastrado"
        rota = render_template("mensagem.html", mensagem=mensagem)

    return rota
    
def login_usuario(email, senha):
    checkEmail = checarEmail(email)
    if checkEmail["resultado"] == True:
        id_usuario = checkEmail["id_usuario"]
        usuario = procurar_usuario_id(id_usuario)
        checkSenha = checarSenha(usuario["senha_hash"], senha)
        if checkSenha == True:
            session["login"] = True
            session["user_id"] = usuario["id"]
            rota = redirect("/")
        else:
            mensagem = "senha incorreta"
            rota = render_template("mensagem.html", mensagem=mensagem) 
    else:
        mensagem = "email incorreto"
        rota = render_template("mensagem.html", mensagem=mensagem)

    return rota

def adicionarProduto(titulo, descricao, valor, caminho_imagem, id_usuario):
    sql = f"""insert into produto (titulo, descricao, valor, imagem, idusuario) values ('{titulo}', '{descricao}', {valor}, '{caminho_imagem}', {id_usuario})"""
    cursor.execute(sql)
    connect.commit()

def upload_imagem(UPLOAD_FOLDER, imagem, nomeImagem):
    imagem.save(os.path.join(UPLOAD_FOLDER, nomeImagem))

def procurar_produto_id(id_produto):
    sql = f"""select * from produto where id = {id_produto}"""
    cursor.execute(sql)
    resultado = cursor.fetchone()
    connect.commit()
    produto = {"id_produto":resultado[0],
               "titulo":resultado[1],
               "descricao":resultado[2],
               "valor":resultado[3],
               "imagem":resultado[4],
               "id_usuario_produto":resultado[5]}
    return produto

def procurar_produtos_usuario(user_id):
    sql = f"""select * from produto where idusuario = {user_id}"""
    cursor.execute(sql)
    produtos_usuario = cursor.fetchall()
    if len(produtos_usuario) == 0:
        produtos_usuario = None
    return produtos_usuario

# Modificar / Utilizar

def removerUsuario(id_usuario):
    sql = f"""delete from usuario where id = {id_usuario}"""
    cursor.execute(sql)
    connect.commit()

def quantidadeUsuarios():
    sql = """select id from usuario"""
    cursor.execute(sql)
    resultado = cursor.fetchall()
    return len(resultado)

#Pronto

def listarUsuarios():
    sql = """select id, nome, email from usuario"""
    cursor.execute(sql)
    resultado = cursor.fetchall()
    connect.commit()
    for usuario in resultado:
        print("Id: ", usuario[0],".Nome: ", usuario[1], ".Email: ", usuario[2])

def quantidadeProdutos():
    sql = """select id from produto"""
    cursor.execute(sql)
    resultado = cursor.fetchall()
    return len(resultado)

# Fazer

def removerProduto(self, produto):
    self.produtos.remove(produto)

# Fazer

def listarProdutos(self):
    for produto in self.produtos:
        print(f"Título: {produto.titulo}")
        print(f"Descrição: {produto.descricao}")
        print(f"Valor: {produto.valor}")
        print(f"Nome da Imagem (caminho): {produto.imagem}")
        print()

        
        
