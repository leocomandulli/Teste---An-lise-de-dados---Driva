'''
Aplicação para processamento dos dados 
'''
# Bibliotecas
import matplotlib.pyplot as plt
import pandas as pd
# Importação do models
from model import *


def calcular_faturamento_diario(data_inicio=None, data_fim=None):
    # Obtenção dos dados pelo models
    df_produtos, df_vendas = tratar_dados()

    # Converter a coluna 'DATA' para o tipo datetime
    df_vendas['DATA'] = pd.to_datetime(df_vendas['DATA'], format='%m/%d/%Y')

    # Filtrar por intervalo de datas, se fornecido
    if data_inicio and data_fim:
        # Converter as datas para datetime64[ns]
        data_inicio = pd.to_datetime(data_inicio)
        data_fim = pd.to_datetime(data_fim)
        df_vendas = df_vendas[(df_vendas['DATA'] >= data_inicio) & (df_vendas['DATA'] <= data_fim)]

    # Agrupar por data e SOMAR o faturamento total diário
    faturamento_diario = df_vendas.groupby('DATA')['VALOR_VENDA'].sum().reset_index()

    return faturamento_diario

def melhor_dia_vendas(data_inicio, data_fim):
    """
    Identifica o melhor dia em vendas dentro de um intervalo de datas.

    Parâmetros:
    data_inicio (datetime): Data de início do intervalo.
    data_fim (datetime): Data de fim do intervalo.

    Retorna:
    tuple: (melhor_dia, faturamento, produtos_vendidos)
    """
    df_produtos, df_vendas = tratar_dados()

    # Converter as datas para datetime64[ns]
    data_inicio = pd.to_datetime(data_inicio)
    data_fim = pd.to_datetime(data_fim)

    # Filtrar vendas dentro do intervalo de datas
    df_filtrado = df_vendas[(df_vendas['DATA'] >= data_inicio) & (df_vendas['DATA'] <= data_fim)]

    # Verificar se há dados no intervalo
    if df_filtrado.empty:
        return None, None, None

    # Calcular o faturamento diário
    faturamento_diario = df_filtrado.groupby('DATA')['VALOR_VENDA'].sum().reset_index()

    # Encontrar o melhor dia
    melhor_dia_info = faturamento_diario.loc[faturamento_diario['VALOR_VENDA'].idxmax()]
    melhor_dia = melhor_dia_info['DATA']
    faturamento = melhor_dia_info['VALOR_VENDA']

    # Obter os produtos vendidos no melhor dia
    produtos_vendidos = df_filtrado[df_filtrado['DATA'] == melhor_dia][['ID_PRODUTO', 'VALOR_VENDA']]

    # Relacionar com df_produtos para obter o nome dos produtos
    produtos_vendidos = produtos_vendidos.merge(df_produtos, on='ID_PRODUTO', how='left')[['NOME_PRODUTO', 'VALOR_VENDA']]

    return melhor_dia, faturamento, produtos_vendidos

def dia_mais_vendeu_produto(nome_produto, data_inicio=None, data_fim=None):

    # Obtenção dos dados pelo models
    df_produtos, df_vendas = tratar_dados()

    # Relacionar as vendas com os produtos para obter o nome dos produtos
    df_vendas_com_produtos = df_vendas.merge(df_produtos, on='ID_PRODUTO', how='left')

    # Filtrar apenas as vendas do produto selecionado
    vendas_produto = df_vendas_com_produtos[df_vendas_com_produtos['NOME_PRODUTO'] == nome_produto]

    # Verificar se há vendas do produto
    if vendas_produto.empty:
        return None, None

    # Filtrar por intervalo de datas, se fornecido
    if data_inicio and data_fim:
        data_inicio = pd.to_datetime(data_inicio)
        data_fim = pd.to_datetime(data_fim)
        vendas_produto = vendas_produto[(vendas_produto['DATA'] >= data_inicio) & (vendas_produto['DATA'] <= data_fim)]

    # Agrupar por data e somar o valor vendido do produto
    vendas_produto_por_dia = vendas_produto.groupby('DATA')['VALOR_VENDA'].sum().reset_index()

    # Verificar se há vendas no intervalo
    if vendas_produto_por_dia.empty:
        return None, None

    # Encontrar o dia com o maior valor de vendas do produto
    melhor_dia_info = vendas_produto_por_dia.loc[vendas_produto_por_dia['VALOR_VENDA'].idxmax()]
    data = melhor_dia_info['DATA']
    valor_vendido = melhor_dia_info['VALOR_VENDA']

    return data, valor_vendido

def ranking_produtos_mais_vendidos_em_peso(data_inicio=None, data_fim=None):
    # Obtenção dos dados pelo models
    df_produtos, df_vendas = tratar_dados()

    # Relacionar as vendas com os produtos para obter o peso médio unitário
    df_vendas_com_produtos = df_vendas.merge(df_produtos, on='ID_PRODUTO', how='left')

    # Filtrar por intervalo de datas, se fornecido
    if data_inicio and data_fim:
        data_inicio = pd.to_datetime(data_inicio)
        data_fim = pd.to_datetime(data_fim)
        df_vendas_com_produtos = df_vendas_com_produtos[
            (df_vendas_com_produtos['DATA'] >= data_inicio) & (df_vendas_com_produtos['DATA'] <= data_fim)
        ]

    # Calcular o peso total vendido de cada produto
    df_vendas_com_produtos['PESO_TOTAL'] = df_vendas_com_produtos['VALOR_VENDA'] / df_vendas_com_produtos['PREÇO_KG']
    peso_por_produto = df_vendas_com_produtos.groupby('NOME_PRODUTO')['PESO_TOTAL'].sum().reset_index()

    # Verificar se há dados
    if peso_por_produto.empty:
        return None

    # Ordenar os produtos pelo peso total vendido (em ordem decrescente)
    ranking = peso_por_produto.sort_values(by='PESO_TOTAL', ascending=False)

    return ranking

def calcular_faturamento_por_dia_semana(data_inicio=None, data_fim=None):
    """
    Calcula o faturamento total por dia da semana, com a distribuição percentual dos produtos.
    Retorna um DataFrame com os dados.
    """
    df_produtos, df_vendas = tratar_dados()

    # Filtrar por intervalo de datas, se fornecido
    if data_inicio and data_fim:
        data_inicio = pd.to_datetime(data_inicio)
        data_fim = pd.to_datetime(data_fim)
        df_vendas = df_vendas[(df_vendas['DATA'] >= data_inicio) & (df_vendas['DATA'] <= data_fim)]

    # Adicionar coluna de dia da semana
    df_vendas['DIA_SEMANA'] = df_vendas['DATA'].dt.day_name()

    # Relacionar as vendas com os produtos para obter o nome dos produtos
    df_vendas_com_produtos = df_vendas.merge(df_produtos, on='ID_PRODUTO', how='left')

    # Agrupar por dia da semana e produto, somando o valor vendido
    faturamento_por_dia_semana = df_vendas_com_produtos.groupby(['DIA_SEMANA', 'NOME_PRODUTO'])['VALOR_VENDA'].sum().reset_index()

    # Calcular o total por dia da semana
    total_por_dia_semana = faturamento_por_dia_semana.groupby('DIA_SEMANA')['VALOR_VENDA'].sum().reset_index()

    # Calcular a porcentagem de cada produto no faturamento diário
    faturamento_por_dia_semana = faturamento_por_dia_semana.merge(total_por_dia_semana, on='DIA_SEMANA', suffixes=('', '_TOTAL'))
    faturamento_por_dia_semana['PORCENTAGEM'] = (faturamento_por_dia_semana['VALOR_VENDA'] / faturamento_por_dia_semana['VALOR_VENDA_TOTAL']) * 100

    return faturamento_por_dia_semana

def pior_dia_vendas(data_inicio=None, data_fim=None):
    """
    Identifica o pior dia em vendas dentro de um intervalo de datas.
    Retorna a data e o faturamento do pior dia.
    """
    df_produtos, df_vendas = tratar_dados()

    # Filtrar por intervalo de datas, se fornecido
    if data_inicio and data_fim:
        data_inicio = pd.to_datetime(data_inicio)
        data_fim = pd.to_datetime(data_fim)
        df_vendas = df_vendas[(df_vendas['DATA'] >= data_inicio) & (df_vendas['DATA'] <= data_fim)]

    # Calcular o faturamento diário
    faturamento_diario = df_vendas.groupby('DATA')['VALOR_VENDA'].sum().reset_index()

    # Verificar se há dados
    if faturamento_diario.empty:
        return None, None

    # Encontrar o pior dia
    pior_dia_info = faturamento_diario.loc[faturamento_diario['VALOR_VENDA'].idxmin()]
    pior_dia = pior_dia_info['DATA']
    faturamento = pior_dia_info['VALOR_VENDA']

    return pior_dia, faturamento

def calcular_media_faturamento_diario(data_inicio=None, data_fim=None):
    """
    Calcula a média de faturamento diário no período selecionado.
    """
    df_produtos, df_vendas = tratar_dados()
    # Filtrar por intervalo de datas, se fornecido
    if data_inicio and data_fim:
        data_inicio = pd.to_datetime(data_inicio)
        data_fim = pd.to_datetime(data_fim)
        df_vendas = df_vendas[(df_vendas['DATA'] >= data_inicio) & (df_vendas['DATA'] <= data_fim)]

    # Agrupar vendas por dia e somar o faturamento diário
    faturamento_diario = df_vendas.groupby(df_vendas['DATA'].dt.date)['VALOR_VENDA'].sum()

    # Calcular a média do faturamento diário
    media_faturamento = faturamento_diario.mean()
    return media_faturamento

def traduzir_dia_semana(dia_ingles):
    """
    Traduz o dia da semana de inglês para português.
    """
    dias = {
        "Monday": "Segunda-feira",
        "Tuesday": "Terça-feira",
        "Wednesday": "Quarta-feira",
        "Thursday": "Quinta-feira",
        "Friday": "Sexta-feira",
        "Saturday": "Sábado",
        "Sunday": "Domingo"
    }
    return dias.get(dia_ingles, dia_ingles)