import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates
from views import *


def plotar_faturamento_diario(data_inicio=None, data_fim=None):
    """
    Gera um gráfico da evolução do faturamento diário com linha de tendência e média móvel.
    Retorna a figura do gráfico.
    """
    # Obter o faturamento diário
    faturamento_diario = calcular_faturamento_diario(data_inicio, data_fim)

    # Verificar se há dados
    if faturamento_diario.empty:
        st.warning("Nenhum dado encontrado no intervalo selecionado.")
        return None

    # Extrair datas e valores de faturamento
    datas = faturamento_diario['DATA']
    valores = faturamento_diario['VALOR_VENDA']

    # Converter datas para números (dias desde a primeira data)
    dias = (datas - datas.min()).dt.days

    # Calcular a linha de tendência (regressão linear)
    coeficientes = np.polyfit(dias, valores, deg=1)  # Coeficientes da regressão linear
    tendencia = np.polyval(coeficientes, dias)  # Valores da linha de tendência

    # Inclinação da reta (coeficiente angular)
    inclinacao = coeficientes[0]

    # Calcular a tendência em termos percentuais
    # Variação percentual = (inclinacao * dias_totais / valor_inicial) * 100
    dias_totais = dias.max()  # Número total de dias no período
    valor_inicial = valores.iloc[0]  # Primeiro valor de faturamento
    tendencia_percentual = (inclinacao * dias_totais / valor_inicial) * 100  # Percentual de variação

    # Exibir o valor da tendência percentual
    st.write(f"Tendência de variação percentual do faturamento: {tendencia_percentual:.2f}% ao longo do período.")

    # Calcular a média móvel (janela de 7 dias)
    window_size = 7  # Tamanho da janela para a média móvel
    media_movel = np.convolve(valores, np.ones(window_size)/window_size, mode='valid')
    datas_media_movel = datas[window_size - 1:]  # Ajustar as datas para a média móvel

    # Configurar o estilo do gráfico
    plt.style.use('ggplot')  # Estilo moderno e bonito
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plotar a evolução do faturamento
    ax.plot(datas, valores, marker='o', linestyle='-', color='dodgerblue', label='Faturamento Diário')

    # Plotar a linha de tendência
    ax.plot(datas, tendencia, linestyle='--', color='red', label='Linha de Tendência')

    # Plotar a média móvel
    ax.plot(datas_media_movel, media_movel, linestyle='-', color='green', label=f'Média Móvel ({window_size} dias)')

    # Configurar o eixo X para mostrar datas de forma legível
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Formato da data
    ax.xaxis.set_major_locator(mdates.MonthLocator())  # Mostrar uma marcação por mês
    plt.xticks(rotation=45)  # Rotacionar as datas para melhor visualização

    # Adicionar título e labels
    ax.set_title('Evolução do Faturamento Diário', fontsize=16, pad=20)
    ax.set_xlabel('Data', fontsize=12)
    ax.set_ylabel('Faturamento Total (R$)', fontsize=12)

    # Adicionar grid e legendas
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend(loc='upper left', fontsize=12)

    # Ajustar layout para evitar cortes
    plt.tight_layout()

    # Retornar a figura
    return fig



def plotar_grafico_pizza(ranking):
    """
    Plota um gráfico de pizza com a distribuição do faturamento por produto.
    Produtos com menos de 3% são agrupados em "Outros".
    """
    # Agrupar produtos com menos de 3% em "Outros"
    ranking['PORCENTAGEM'] = (ranking['PESO_TOTAL'] / ranking['PESO_TOTAL'].sum()) * 100
    outros = ranking[ranking['PORCENTAGEM'] < 3]
    principais = ranking[ranking['PORCENTAGEM'] >= 3]

    if not outros.empty:
        outros_total = outros['PESO_TOTAL'].sum()
        outros_df = pd.DataFrame({'NOME_PRODUTO': ['Outros'], 'PESO_TOTAL': [outros_total]})
        principais = pd.concat([principais, outros_df], ignore_index=True)

    # Plotar o gráfico de pizza
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(principais['PESO_TOTAL'], labels=principais['NOME_PRODUTO'], autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Garante que o gráfico seja um círculo
    return fig

def exibir_ranking_produtos_mais_vendidos_em_peso(data_inicio=None, data_fim=None):
    """
    Exibe um ranking dos produtos mais vendidos em peso de forma visual e amigável.
    O maior peso fica à esquerda e o menor à direita.

    Parâmetros:
    data_inicio (datetime): Data de início do intervalo (opcional).
    data_fim (datetime): Data de fim do intervalo (opcional).
    """
    # Obter o ranking dos produtos mais vendidos em peso
    ranking = ranking_produtos_mais_vendidos_em_peso(data_inicio, data_fim)

    # Verificar se há dados
    if ranking is None or ranking.empty:
        st.warning("Nenhum dado encontrado no intervalo selecionado.")
        return

    # Ordenar o ranking para que o maior peso fique à esquerda
    ranking = ranking.sort_values(by='PESO_TOTAL', ascending=True)  # Ordena do menor para o maior
    ranking = ranking.reset_index(drop=True)  # Resetar o índice para garantir a ordem correta

    # Exibir o ranking como um gráfico de barras
    st.subheader("Ranking dos Produtos Mais Vendidos em Peso")
    st.bar_chart(ranking.set_index('NOME_PRODUTO'))

def plotar_faturamento_por_dia_semana(data_inicio=None, data_fim=None):
    """
    Plota um gráfico de barras com o faturamento por dia da semana e subdivisão por produtos.
    """
    df_vendas = st.session_state.df_vendas
    df_produtos = st.session_state.df_produtos

    # Filtrar por intervalo de datas
    if data_inicio and data_fim:
        data_inicio = pd.to_datetime(data_inicio)
        data_fim = pd.to_datetime(data_fim)
        df_vendas = df_vendas[(df_vendas['DATA'] >= data_inicio) & (df_vendas['DATA'] <= data_fim)]

    # Juntar com produtos e traduzir dias
    df = df_vendas.merge(df_produtos, on='ID_PRODUTO')
    df['DIA_SEMANA'] = df['DATA'].dt.strftime('%A').apply(traduzir_dia_semana)

    # Agrupar por dia e produto
    faturamento = df.groupby(['DIA_SEMANA', 'NOME_PRODUTO'])['VALOR_VENDA'].sum().unstack().fillna(0)
    
    # Ordenar dias
    ordem_dias = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", 
                "Sexta-feira", "Sábado", "Domingo"]
    faturamento = faturamento.reindex(ordem_dias)

    # Plotar
    fig, ax = plt.subplots(figsize=(12, 6))
    faturamento.plot(kind='bar', stacked=True, ax=ax, colormap='tab20')
    
    ax.set_title('Faturamento por Dia da Semana e Produto', fontsize=16, pad=20)
    ax.set_xlabel('Dia da Semana', fontsize=12)
    ax.set_ylabel('Faturamento Total (R$)', fontsize=12)
    ax.legend(title='Produtos', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    return fig