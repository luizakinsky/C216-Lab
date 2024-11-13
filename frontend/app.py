from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests
import os

app = Flask(__name__)

# Definindo as variáveis de ambiente
API_BASE_URL = "http://backend:8000"

# Rota para a página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Rota para exibir o formulário de cadastro
@app.route('/cadastro', methods=['GET'])
def inserir_filme_form():
    return render_template('cadastro.html')

# Rota para enviar os dados do formulário de cadastro para a API
@app.route('/inserir', methods=['POST'])
def inserir_filme():
    titulo = request.form['titulo']
    diretor = request.form['diretor']
    quantidade = int(request.form['quantidade'])  # Para garantir que é um inteiro
    preco = float(request.form['preco'])          # Para garantir que é um float

    payload = {
        'titulo': titulo,
        'diretor': diretor,
        'quantidade': quantidade,
        'preco': preco
    }

    response = requests.post(f'{API_BASE_URL}/api/v1/filmes/', json=payload)
    
    if response.status_code == 201:
        return redirect(url_for('listar_filmes'))
    else:
        return "Erro ao inserir filme", 500

# Rota para listar todos os filmes
@app.route('/estoque', methods=['GET'])
def listar_filmes():
    response = requests.get(f'{API_BASE_URL}/api/v1/filmes/')
    try:
        filmes = response.json()
    except:
        filmes = []
    return render_template('estoque.html', filmes=filmes)

# Rota para exibir o formulário de edição de filmes
@app.route('/atualizar/<int:filme_id>', methods=['GET'])
def atualizar_filme_form(filme_id):
    response = requests.get(f"{API_BASE_URL}/api/v1/filmes/")
    #filtrando apenas o filme correspondente ao ID
    filmes = [filme for filme in response.json() if filme['id'] == filme_id]
    if len(filmes) == 0:
        return "filme não encontrado", 404
    filme = filmes[0]
    return render_template('atualizar.html', filme=filme)

# Rota para enviar os dados do formulário de edição de filme para a API
@app.route('/atualizar/<int:filme_id>', methods=['POST'])
def atualizar_filme(filme_id):
    titulo = request.form['titulo']
    diretor = request.form['diretor']
    quantidade = request.form['quantidade']
    preco = request.form['preco']

    payload = {
        'id': filme_id,
        'titulo': titulo,
        'diretor': diretor,
        'quantidade': quantidade,
        'preco': preco
    }

    response = requests.patch(f"{API_BASE_URL}/api/v1/filmes/{filme_id}", json=payload)
    
    if response.status_code == 200:
        return redirect(url_for('listar_filmes'))
    else:
        return "Erro ao atualizar filme", 500

# Rota para exibir o formulário de edição de filme
@app.route('/vender/<int:filme_id>', methods=['GET'])
def vender_filme_form(filme_id):
    response = requests.get(f"{API_BASE_URL}/api/v1/filmes/")
    #filtrando apenas o filme correspondente ao ID
    filmes = [filme for filme in response.json() if filme['id'] == filme_id]
    if len(filmes) == 0:
        return "filme não encontrado", 404
    filme = filmes[0]
    return render_template('vender.html', filme=filme)

# Rota para vender um filme
@app.route('/vender/<int:filme_id>', methods=['POST'])
def vender_filme(filme_id):
    quantidade = request.form['quantidade']

    payload = {
        'quantidade': quantidade
    }

    response = requests.put(f"{API_BASE_URL}/api/v1/filmes/{filme_id}/vender/", json=payload)
    
    if response.status_code == 200:
        return redirect(url_for('listar_filmes'))
    else:
        return "Erro ao vender filme", 500

# Rota para listar todas as vendas
@app.route('/vendas', methods=['GET'])
def listar_vendas():
    response = requests.get(f"{API_BASE_URL}/api/v1/vendas/")
    try:
        vendas = response.json()
    except:
        vendas = []
    #salvando nomes dos filmes vendidos
    total_vendas = 0
    for venda in vendas:
        total_vendas += float(venda['valor_venda'])
    return render_template('vendas.html', vendas=vendas, total_vendas=total_vendas)

# Rota para excluir um filme
@app.route('/excluir/<int:filme_id>', methods=['POST'])
def excluir_filme(filme_id):
    response = requests.delete(f"{API_BASE_URL}/api/v1/filmes/{filme_id}")
    
    if response.status_code == 200  :
        return redirect(url_for('listar_filmes'))
    else:
        return "Erro ao excluir filme", 500

#Rota para resetar o database
@app.route('/reset-database', methods=['GET'])
def resetar_database():
    response = requests.delete(f"{API_BASE_URL}/api/v1/filmes/")
    
    if response.status_code == 200  :
        return render_template('confirmacao.html')
    else:
        return "Erro ao resetar o database", 500


if __name__ == '__main__':
    app.run(debug=True, port=3000, host='0.0.0.0')
