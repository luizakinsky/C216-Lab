# Descrição do Problema
# Você foi contratado por uma pequena loja para criar um sistema básico de gerenciamento de estoque. 
# Este sistema deve ser capaz de:

# Cadastrar Itens
def cadastro(estoque):
    nome = input("Digite o nome do produto: ")
    quantidade = int(input("Digite a quantidade: "))
    preco = float(input("Digite o preço: "))
    
    if nome in estoque:
        print(f"Produto '{nome}' já cadastrado. Atualizando a quantidade.")
        estoque[nome]['quantidade'] += quantidade
    else:
        estoque[nome] = {'quantidade': quantidade, 'preco': preco}
    
    print(f"Item '{nome}' cadastrado/atualizado com sucesso!\n")


# Listar Itens
def listagem(estoque):
    if estoque:
        print("\nProdutos no estoque:")
        for nome, detalhes in estoque.items():
            print(f"Nome: {nome}, Quantidade: {detalhes['quantidade']}, Preço: R${detalhes['preco']:.2f}")
    else:
        print("Estoque vazio!\n")


# Consultar Itens
def consulta(estoque):
    nome = input("Digite o nome do produto para consulta: ")
    if nome in estoque:
        detalhes = estoque[nome]
        print(f"Nome: {nome}, Quantidade: {detalhes['quantidade']}, Preço: R${detalhes['preco']:.2f}\n")
    else:
        print(f"Produto '{nome}' não encontrado no estoque.\n")


# Vender Itens
def venda(estoque):
    nome = input("Digite o nome do produto para venda: ")
    if nome in estoque:
        quantidade = int(input("Digite a quantidade a ser vendida: "))
        if quantidade <= estoque[nome]['quantidade']:
            estoque[nome]['quantidade'] -= quantidade
            print(f"{quantidade} unidade(s) de '{nome}' vendida(s).")
            print(f"Valor total: R${quantidade * estoque[nome]['preco']:.2f}\n")
            if estoque[nome]['quantidade'] == 0:
                del estoque[nome]
                print(f"Produto '{nome}' esgotado e removido do estoque.\n")
        else:
            print(f"Quantidade insuficiente em estoque. Disponível: {estoque[nome]['quantidade']} unidade(s).\n")
    else:
        print(f"Produto '{nome}' não encontrado no estoque.\n")

def main():
    estoque = {}
    while True:
        print("\nMenu:")
        print("1. Cadastrar Produtos")
        print("2. Listar Produtos")
        print("3. Consultar Produtos")
        print("4. Vender Produtos")
        print("5. Sair")
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == '1':
            cadastro(estoque)
        elif opcao == '2':
            listagem(estoque)
        elif opcao == '3':
            consulta(estoque)
        elif opcao == '4':
            venda(estoque)
        elif opcao == '5':
            print("Saindo do sistema!")
            break
        else:
            print("Opção inválida. Tente novamente.\n")

if __name__ == "__main__":
    main()