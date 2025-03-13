import streamlit as st
from template import *
from views import *
from model import *

def main():
    # Configuração inicial da página
    st.set_page_config(
        page_title="Feira Analytics",
        page_icon="📊",
        layout="wide"
    )
    
    # CSS personalizado para compactar elementos
    st.markdown("""
        <style>
            .main {padding: 1rem !important;}
            .block-container {padding-top: 1rem !important;}
            .header-title {font-size: 2rem !important; margin-bottom: 0.5rem !important;}
            .metric-box {padding: 1rem !important; margin: 0.25rem !important;}
            .section-title {font-size: 1.25rem !important; margin-bottom: 0.5rem !important;}
            .stDataFrame {max-height: 200px; overflow-y: auto;}
            .stPlotlyChart {height: 250px !important;}
            .stMetric {padding: 0.5rem !important;}
            .stTabs [data-baseweb="tab-list"] {gap: 0.5rem;}
            .stTabs [data-baseweb="tab"] {padding: 0.5rem 1rem; border-radius: 4px;}
        </style>
    """, unsafe_allow_html=True)

    # Título principal compacto
    st.markdown('<h1 class="header-title">📈 Feira Analytics</h1>', unsafe_allow_html=True)

    # Carregar dados uma única vez e armazenar em session_state
    if 'df_produtos' not in st.session_state or 'df_vendas' not in st.session_state:
        st.session_state.df_produtos, st.session_state.df_vendas = tratar_dados()

    # Sidebar compacta
    with st.sidebar:
        st.header("⚙️ Filtros")
        
        # Filtro temporal
        data_min = st.session_state.df_vendas['DATA'].min()
        data_max = st.session_state.df_vendas['DATA'].max()
        data_inicio = st.date_input("Data de início", value=data_min, 
                                  min_value=data_min, max_value=data_max)
        data_fim = st.date_input("Data final", value=data_max, 
                               min_value=data_min, max_value=data_max)

        # Previsão de faturamento futuro
        st.markdown("---")
        st.header("🔮 Previsão de Faturamento")
        if st.button("Calcular Previsão"):
            previsoes = prever_faturamento_futuro(data_inicio, data_fim, dias_futuros=[14, 30])
            
            st.markdown(f"""
                **Próximos 14 Dias:**
                - Faturamento Previsto: R$ {previsoes['proximos_14_dias']:,.2f}
                
                **Próximos 30 Dias:**
                - Faturamento Previsto: R$ {previsoes['proximos_30_dias']:,.2f}
            """)
             
    # Layout principal usando colunas
    col1, col2 = st.columns([2, 1], gap="medium")

    with col1:
        # Gráfico principal compacto
        st.markdown('<h3 class="section-title">📅 Evolução Diária</h3>', unsafe_allow_html=True)
        fig = plotar_faturamento_diario(data_inicio, data_fim)
        st.pyplot(fig, use_container_width=True)

        # Gráfico de faturamento por dia da semana
        st.markdown('<h3 class="section-title">🗓️ Faturamento Semanal</h3>', unsafe_allow_html=True)
        fig_dia_semana = plotar_faturamento_por_dia_semana(data_inicio, data_fim)
        st.pyplot(fig_dia_semana, use_container_width=True)

    with col2:
        # Seção de Performance com abas
        st.markdown('<h3 class="section-title">🏆 Performance</h3>', unsafe_allow_html=True)
        
        # Abas para alternar entre visão geral e análise de produtos
        tab1, tab2 = st.tabs(["📊 Visão Geral", "🧪 Análise de Produtos"])

        with tab1:
            # Melhor e Pior dia de vendas
            melhor_dia, faturamento_melhor, _ = melhor_dia_vendas(data_inicio, data_fim)
            pior_dia, faturamento_pior = pior_dia_vendas(data_inicio, data_fim)
            media_faturamento = calcular_media_faturamento_diario(data_inicio, data_fim)
            faturamento_total = calcular_faturamento_total(data_inicio, data_fim)  # Novo cálculo

            # Layout em duas colunas
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 🎯 Melhor Dia")
                if melhor_dia is not None:
                    st.markdown(f"**📅 Data:** {melhor_dia.strftime('%d/%m/%Y')}")
                    st.markdown(f"**🗓️ Dia da Semana:** {traduzir_dia_semana(melhor_dia.strftime('%A'))}")
                    st.markdown(f"**💰 Faturamento:** R$ {faturamento_melhor:,.2f}")
                    diferenca = faturamento_melhor - media_faturamento
                    st.markdown(f"**📊 Vs Média:** <span style='color: #2e7d32;'>+R$ {diferenca:,.2f}</span>", 
                                unsafe_allow_html=True)
                else:
                    st.warning("Nenhum dado encontrado para o período selecionado.")

            with col2:
                st.markdown("### 📉 Pior Dia")
                if pior_dia is not None:
                    st.markdown(f"**📅 Data:** {pior_dia.strftime('%d/%m/%Y')}")
                    st.markdown(f"**🗓️ Dia da Semana:** {traduzir_dia_semana(pior_dia.strftime('%A'))}")
                    st.markdown(f"**💰 Faturamento:** R$ {faturamento_pior:,.2f}")
                    diferenca = faturamento_pior - media_faturamento
                    st.markdown(f"**📊 Vs Média:** <span style='color: #d32f2f;'>-R$ {abs(diferenca):,.2f}</span>", 
                                unsafe_allow_html=True)
                else:
                    st.warning("Nenhum dado encontrado para o período selecionado.")

            # Faturamento Total
            st.markdown("---")
            st.markdown(f"### 💰 Faturamento Total no Período")
            st.markdown(f"**Total:** R$ {faturamento_total:,.2f}")

            # Gráfico de Pizza
            st.markdown("---")
            st.markdown("### 🍕 Distribuição de Faturamento")
            ranking = ranking_produtos_mais_vendidos_em_peso(data_inicio, data_fim)
            if not ranking.empty:
                fig_pizza = plotar_grafico_pizza(ranking)
                st.pyplot(fig_pizza, use_container_width=True)
                st.caption("Produtos com menos de 3% do faturamento foram agrupados em 'Outros'")
            else:
                st.warning("Nenhum dado encontrado para o período selecionado.")

        with tab2:
            # Seleção de produtos dentro da aba de análise
            produtos_disponiveis = st.session_state.df_produtos['NOME_PRODUTO'].unique().tolist()
            produtos_selecionados = st.multiselect(
                "Selecione produtos para análise:",
                options=produtos_disponiveis
            )

            if produtos_selecionados:
                # Análise de produtos em lista vertical
                for produto in produtos_selecionados:
                    with st.expander(f"📊 {produto}"):
                        data_produto, valor_produto = dia_mais_vendeu_produto(produto, data_inicio, data_fim)
                        if data_produto:
                            st.metric("Data de Pico", data_produto.strftime('%d/%m/%Y'))
                            st.metric("Faturamento Máximo", f"R$ {valor_produto:.2f}")
                        else:
                            st.warning("Sem dados para este período")
            else:
                st.warning("Selecione produtos para análise.")

if __name__ == "__main__":
    main()