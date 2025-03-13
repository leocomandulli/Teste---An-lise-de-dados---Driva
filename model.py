'''
Aplicação para fazer as leituras da base de dados
'''
import pandas as pd

# Função para converter o URL de edição para o URL de exportação CSV
def converte_para_csv_url(url):
    # Extrai o ID da planilha e o GID
    base_url = url.split('/edit')[0]  # Remove tudo após '/edit'
    gid = url.split('gid=')[1]  # Extrai o GID
    # Monta o URL de exportação CSV
    csv_url = f"{base_url}/export?format=csv&gid={gid}"
    return csv_url

# Função para leitura dos dados
def ler_dados_gs():
    # URLs das planilhas (substitua pelos seus URLs)
    url_produtos = "https://docs.google.com/spreadsheets/d/1HyPn009-K7LR_BGh24JPXGGrLl-c0K4FvNe7-he6BJg/edit?gid=1250817030#gid=1250817030"
    url_vendas = "https://docs.google.com/spreadsheets/d/1HyPn009-K7LR_BGh24JPXGGrLl-c0K4FvNe7-he6BJg/edit?gid=60685992#gid=60685992"


    # Converter os URLs para o formato de exportação CSV
    csv_url_produtos = converte_para_csv_url(url_produtos)
    csv_url_vendas = converte_para_csv_url(url_vendas)

    # Ler os dados
    df_produtos = pd.read_csv(csv_url_produtos)
    df_vendas = pd.read_csv(csv_url_vendas)

    return df_produtos, df_vendas

## Função para tratamento dos dados 
def tratar_dados():

    df_produtos, df_vendas = ler_dados_gs()
    # Tratamento do DataFrame de produtos
    df_produtos['PREÇO_KG'] = df_produtos['PREÇO_KG'].str.replace(',', '.').astype(float)
    df_produtos['PESO_MEDIO_UNITARIO_KG'] = df_produtos['PESO_MEDIO_UNITARIO_KG'].str.replace(',', '.').astype(float)

    # Tratamento do DataFrame de vendas
    df_vendas['VALOR_VENDA'] = df_vendas['VALOR_VENDA'].str.replace(',', '.').astype(float)
    df_vendas['DATA'] = pd.to_datetime(df_vendas['DATA'], format='%m/%d/%Y')

    return df_produtos, df_vendas

# Função para teste 
def test_model():
    df_produtos, df_vendas = tratar_dados()

    print("Produtos:")
    print(df_produtos)

    print("\nVendas:")
    print(df_vendas)

if __name__ == "__main__":
    test_model()