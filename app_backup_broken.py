"""
Dashboard de Análise Financeira Corporativa - Aplicação Principal
Versão modularizada com arquitetura limpa
"""

import streamlit as st
from financial_analyzer import FinancialAnalyzer
from config.settings import AppConfig
from utils.data_loader import carregar_dados
from pages.page_manager import PageManager

# Configuração da página usando módulo centralizado
AppConfig.configure_page()

def main():
    """Função principal da aplicação"""
    # Inicializar dados e analyzer
    if 'df_original' not in st.session_state:
        st.session_state.df_original = carregar_dados()
        st.session_state.financial_analyzer = FinancialAnalyzer(st.session_state.df_original.copy())
    
    # Criar navegação
    st.sidebar.title("🧭 Navegação")
    
    # Usar configuração centralizada para navegação
    paginas = AppConfig.NAVIGATION
    
    pagina_selecionada = st.sidebar.radio(
        "Selecione a análise:",
        list(paginas.keys())
    )
    
    # Obter dados e analyzer
    df = st.session_state.df_original
    financial_analyzer = st.session_state.financial_analyzer
    
    # Criar sidebar com informações (será movido para cada página)
    criar_sidebar(df, financial_analyzer)
    
    # Inicializar gerenciador de páginas
    page_manager = PageManager()
    
    # Renderizar página selecionada usando o gerenciador
    page_key = AppConfig.get_page_value(pagina_selecionada)
    page_manager.render_page(page_key, df, financial_analyzer)

# Executar a aplicação
if __name__ == "__main__":
    main()
    """
    Cria a barra lateral com informações da empresa e filtros
    """
    st.sidebar.title("🏢 Análise Financeira")
    
    # Informações gerais
    st.sidebar.subheader("📊 Resumo Executivo")
    
    anos_disponiveis = sorted(df['Ano'].unique(), reverse=True)
    ano_selecionado = st.sidebar.selectbox("Selecione o Ano para Análise:", anos_disponiveis)
    
    # KPIs do ano selecionado
    dados_ano = df[df['Ano'] == ano_selecionado].iloc[0]
    
    # Função auxiliar para formatar valores monetários de forma segura
    def format_currency(value):
        try:
            # Converter para float se necessário
            if isinstance(value, str):
                value = float(value.replace('.', '').replace(',', '.'))
            return f"R$ {float(value):,.0f}".replace(',', '.')
        except:
            return f"R$ {value}"
    
    # Função auxiliar para formatar percentuais de forma segura
    def format_percentage(value):
        try:
            if isinstance(value, str):
                value = float(value.replace(',', '.'))
            return f"{float(value):.1%}"
        except:
            return f"{value}"
    
    # Função auxiliar para formatar números decimais de forma segura
    def format_decimal(value):
        try:
            if isinstance(value, str):
                value = float(value.replace(',', '.'))
            return f"{float(value):.2f}"
        except:
            return f"{value}"
    
    st.sidebar.metric(
        "� Receita Líquida", 
        format_currency(dados_ano['Receita Líquida'])
    )
    
    st.sidebar.metric(
        "💎 Lucro Líquido", 
        format_currency(dados_ano['Lucro Líquido'])
    )
    
    st.sidebar.metric(
        "📈 ROE", 
        format_percentage(dados_ano['Rentabilidade do Patrimônio Líquido (ROE) '])
    )
    
    st.sidebar.metric(
        "🎯 ROA", 
        format_percentage(dados_ano['Rentabilidade do Ativo (ROA ou ROI)'])
    )
    
    st.sidebar.metric(
        "🛡️ Liquidez Corrente", 
        format_decimal(dados_ano['Liquidez Corrente (LC) '])
    )
    
    # Indicadores de alerta
    st.sidebar.subheader("🚨 Indicadores de Atenção")
    
    # Converter valores para float de forma segura
    try:
        liquidez = float(dados_ano['Liquidez Corrente (LC) ']) if isinstance(dados_ano['Liquidez Corrente (LC) '], str) else dados_ano['Liquidez Corrente (LC) ']
    except:
        liquidez = 0
    
    try:
        endividamento = float(dados_ano['Endividamento Geral (EG)']) if isinstance(dados_ano['Endividamento Geral (EG)'], str) else dados_ano['Endividamento Geral (EG)']
    except:
        endividamento = 0
    
    if liquidez < 1.0:
        st.sidebar.error(f"⚠️ Liquidez Corrente baixa: {liquidez:.2f}")
    elif liquidez < 1.5:
        st.sidebar.warning(f"⚡ Liquidez Corrente moderada: {liquidez:.2f}")
    else:
        st.sidebar.success(f"✅ Liquidez Corrente saudável: {liquidez:.2f}")
    
    if endividamento > 0.7:
        st.sidebar.error(f"⚠️ Alto endividamento: {endividamento:.1%}")
    elif endividamento > 0.5:
        st.sidebar.warning(f"⚡ Endividamento moderado: {endividamento:.1%}")
    else:
        st.sidebar.success(f"✅ Endividamento controlado: {endividamento:.1%}")
    
    return ano_selecionado

# Função para aplicar filtros aos dados
def aplicar_filtros(df, data_inicio, data_fim, tipos, categorias):
    """
    Aplica os filtros selecionados ao DataFrame
    """
    df_filtrado = df.copy()
    
    # Filtro por período
    df_filtrado = df_filtrado[
        (df_filtrado['Data'].dt.date >= data_inicio) &
        (df_filtrado['Data'].dt.date <= data_fim)
    ]
    
    # Filtro por tipo
    if tipos:
        df_filtrado = df_filtrado[df_filtrado['Tipo'].isin(tipos)]
    
    # Filtro por categoria
    if categorias:
        df_filtrado = df_filtrado[df_filtrado['Categoria'].isin(categorias)]
    
    return df_filtrado

# Função para calcular KPIs
def calcular_kpis(df_filtrado):
    """
    Calcula os KPIs principais
    """
    receita_total = df_filtrado[df_filtrado['Tipo'] == 'Receita']['Valor'].sum()
    despesa_total = df_filtrado[df_filtrado['Tipo'] == 'Despesa']['Valor'].sum()
    saldo = receita_total - despesa_total
    
    return {
        'receita_total': receita_total,
        'despesa_total': despesa_total,
        'saldo': saldo
    }

# Função para exibir KPIs
def exibir_kpis(df_filtrado):
    """
    Exibe os KPIs principais
    """
    col1, col2, col3 = st.columns(3)
    
    with col1:
        receita_total = df_filtrado[df_filtrado['Tipo'] == 'Receita']['Valor'].sum()
        st.metric(
            label="Receita Total",
            value=f"R$ {receita_total:,.2f}",
            delta=None
        )
    
    with col2:
        despesa_total = df_filtrado[df_filtrado['Tipo'] == 'Despesa']['Valor'].sum()
        st.metric(
            label="Despesa Total",
            value=f"R$ {despesa_total:,.2f}",
            delta=None
        )
    
    with col3:
        saldo = receita_total - despesa_total
        delta_saldo = saldo if saldo != 0 else None
        st.metric(
            label="Saldo (Lucro/Prejuízo)",
            value=f"R$ {saldo:,.2f}",
            delta=delta_saldo
        )

# Função principal do dashboard
def main():
    """
    Função principal que orquestra todo o dashboard com navegação por páginas
    """
    # Inicializar dados financeiros
    if 'df_original' not in st.session_state:
        st.session_state.df_original = carregar_dados_financeiros()
        st.session_state.financial_analyzer = FinancialAnalyzer(st.session_state.df_original.copy())
    
    # Criar navegação
    st.sidebar.title("🧭 Navegação")
    
    paginas = {
        "📊 Dashboard Executivo": "dashboard",
        "📈 Análise de Rentabilidade": "rentabilidade", 
        "🛡️ Análise de Liquidez": "liquidez",
        "🏦 Estrutura de Capital": "capital",
        "⏱️ Ciclo Financeiro": "ciclo",
        "� Análise DuPont": "dupont",
        "🌡️ Visão Geral (Heatmap)": "heatmap",
        "🤖 Chat com IA": "ai_chat"
    }
    
    pagina_selecionada = st.sidebar.radio(
        "Selecione a análise:",
        list(paginas.keys())
    )
    
    # Obter dados e analyzer
    df = st.session_state.df_original
    financial_analyzer = st.session_state.financial_analyzer
    
    # Criar sidebar com informações
    ano_selecionado = criar_sidebar(df, financial_analyzer)
    
    # Renderizar página selecionada
    if paginas[pagina_selecionada] == "dashboard":
        render_dashboard_executivo(df, financial_analyzer)
    elif paginas[pagina_selecionada] == "rentabilidade":
        render_analise_rentabilidade(df, financial_analyzer)
    elif paginas[pagina_selecionada] == "liquidez":
        render_analise_liquidez(df, financial_analyzer)
    elif paginas[pagina_selecionada] == "capital":
        render_estrutura_capital(df, financial_analyzer)
    elif paginas[pagina_selecionada] == "ciclo":
        render_ciclo_financeiro(df, financial_analyzer)
    elif paginas[pagina_selecionada] == "dupont":
        render_analise_dupont(df, financial_analyzer)
    elif paginas[pagina_selecionada] == "heatmap":
        render_visao_geral(df, financial_analyzer)
    elif paginas[pagina_selecionada] == "ai_chat":
        render_ai_chat_page_financial(df, financial_analyzer)

def render_dashboard_executivo(df, financial_analyzer):
    """
    Dashboard Executivo com KPIs principais
    """
    st.title("📊 Dashboard Executivo - Análise Financeira")
    st.markdown("---")
    
    # KPIs principais
    kpis = financial_analyzer.get_kpis_principais()
    
    st.subheader("📈 KPIs Principais")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "💰 Receita Líquida", 
            f"R$ {kpis['receita_liquida']['atual']:,.0f}".replace(',', '.'),
            f"{kpis['receita_liquida']['variacao']:+.1f}%"
        )
        
        st.metric(
            "📈 ROE", 
            f"{kpis['roe']['atual']:.1%}",
            f"{kpis['roe']['variacao']:+.1f}pp"
        )
    
    with col2:
        st.metric(
            "� Lucro Líquido", 
            f"R$ {kpis['lucro_liquido']['atual']:,.0f}".replace(',', '.'),
            f"{kpis['lucro_liquido']['variacao']:+.1f}%"
        )
        
        st.metric(
            "🎯 ROA", 
            f"{kpis['roa']['atual']:.1%}",
            f"{kpis['roa']['variacao']:+.1f}pp"
        )
    
    with col3:
        st.metric(
            "💧 Margem Líquida", 
            f"{kpis['margem_liquida']['atual']:.1%}",
            f"{kpis['margem_liquida']['variacao']:+.1f}pp"
        )
        
        st.metric(
            "🛡️ Liquidez Corrente", 
            f"{kpis['liquidez_corrente']['atual']:.2f}",
            f"{kpis['liquidez_corrente']['variacao']:+.1f}%"
        )
    
    st.markdown("---")
    
    # Gráfico de evolução patrimonial
    st.subheader("💰 Evolução Patrimonial")
    fig_evolucao = financial_analyzer.create_evolucao_patrimonial()
    st.plotly_chart(fig_evolucao, use_container_width=True)
    
    # Análise de rentabilidade resumida
    st.subheader("📈 Visão Geral da Rentabilidade")
    fig_rent = financial_analyzer.create_rentabilidade_chart()
    st.plotly_chart(fig_rent, use_container_width=True)

def render_analise_rentabilidade(df, financial_analyzer):
    """
    Página especializada em análise de rentabilidade
    """
    st.title("📈 Análise de Rentabilidade")
    st.markdown("---")
    
    # Descrição
    st.markdown("""
    ### 🎯 **Indicadores de Rentabilidade**
    
    - **ROE (Return on Equity)**: Retorno sobre o Patrimônio Líquido
    - **ROA (Return on Assets)**: Retorno sobre os Ativos
    - **Margem Líquida**: Percentual do lucro em relação à receita
    """)
    
    # Gráfico principal de rentabilidade
    fig = financial_analyzer.create_rentabilidade_chart()
    st.plotly_chart(fig, use_container_width=True)
    
    # Análise textual
    anos = df['Ano'].tolist()
    if len(anos) >= 2:
        ano_atual = max(anos)
        ano_anterior = min(anos)
        
        dados_atual = df[df['Ano'] == ano_atual].iloc[0]
        dados_anterior = df[df['Ano'] == ano_anterior].iloc[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"📊 Análise {ano_atual}")
            st.write(f"**ROE:** {dados_atual['Rentabilidade do Patrimônio Líquido (ROE) ']:.1%}")
            st.write(f"**ROA:** {dados_atual['Rentabilidade do Ativo (ROA ou ROI)']:.1%}")
            st.write(f"**Margem Líquida:** {dados_atual['Margem Líquida (ML)']:.1%}")
        
        with col2:
            st.subheader(f"📉 Variação vs {ano_anterior}")
            roe_var = dados_atual['Rentabilidade do Patrimônio Líquido (ROE) '] - dados_anterior['Rentabilidade do Patrimônio Líquido (ROE) ']
            roa_var = dados_atual['Rentabilidade do Ativo (ROA ou ROI)'] - dados_anterior['Rentabilidade do Ativo (ROA ou ROI)']
            ml_var = dados_atual['Margem Líquida (ML)'] - dados_anterior['Margem Líquida (ML)']
            
            st.write(f"**ROE:** {roe_var:+.1f}pp")
            st.write(f"**ROA:** {roa_var:+.1f}pp")
            st.write(f"**Margem Líquida:** {ml_var:+.1f}pp")

def render_analise_liquidez(df, financial_analyzer):
    """
    Página especializada em análise de liquidez
    """
    st.title("🛡️ Análise de Liquidez")
    st.markdown("---")
    
    # Descrição
    st.markdown("""
    ### 💧 **Indicadores de Liquidez**
    
    - **Liquidez Geral (LG)**: Capacidade de pagamento de todas as obrigações
    - **Liquidez Corrente (LC)**: Capacidade de pagamento de obrigações de curto prazo
    - **Liquidez Seca (LS)**: Liquidez corrente excluindo estoques
    - **Liquidez Imediata (LI)**: Capacidade de pagamento imediato
    """)
    
    # Gráfico radar de liquidez
    fig = financial_analyzer.create_liquidez_radar()
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabela com valores
    st.subheader("📋 Valores dos Indicadores")
    liquidez_cols = ['Ano', 'Liquidez Geral (LG)', 'Liquidez Corrente (LC) ', 'Liquidez Seca (LS)', 'Liquidez Imediata (LI)']
    df_liquidez = df[liquidez_cols].round(3)
    st.dataframe(df_liquidez, use_container_width=True)
    
    # Interpretação
    st.subheader("🔍 Interpretação")
    ano_atual = df['Ano'].max()
    dados_atual = df[df['Ano'] == ano_atual].iloc[0]
    
    lc = dados_atual['Liquidez Corrente (LC) ']
    
    if lc >= 1.5:
        st.success(f"✅ **Liquidez Corrente Excelente:** {lc:.2f} - Empresa possui boa capacidade de pagamento")
    elif lc >= 1.0:
        st.warning(f"⚡ **Liquidez Corrente Adequada:** {lc:.2f} - Situação controlada, mas merece atenção")
    else:
        st.error(f"⚠️ **Liquidez Corrente Crítica:** {lc:.2f} - Dificuldades para honrar compromissos de curto prazo")

def render_estrutura_capital(df, financial_analyzer):
    """
    Página especializada em estrutura de capital
    """
    st.title("🏦 Análise da Estrutura de Capital")
    st.markdown("---")
    
    # Descrição
    st.markdown("""
    ### 🏗️ **Indicadores de Endividamento**
    
    - **Endividamento Geral (EG)**: Proporção de recursos de terceiros
    - **Participação de Terceiros (PCT)**: Grau de dependência de capital de terceiros
    - **Composição do Endividamento (CE)**: Concentração das dívidas no curto prazo
    """)
    
    # Gráfico de estrutura de capital
    fig = financial_analyzer.create_estrutura_capital()
    st.plotly_chart(fig, use_container_width=True)
    
    # Análise da estrutura atual
    st.subheader("📊 Análise da Estrutura Atual")
    ano_atual = df['Ano'].max()
    dados = df[df['Ano'] == ano_atual].iloc[0]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("🏦 Endividamento Geral", f"{dados['Endividamento Geral (EG)']:.1%}")
        st.metric("👥 Participação de Terceiros", f"{dados['Participação de Capitais de Terceiros (PCT) – Grau de Endividamento']:.2f}")
    
    with col2:
        st.metric("⏱️ Composição do Endividamento", f"{dados['Composição do Endividamento (CE)']:.1%}")
        
        # Interpretação do endividamento
        eg = dados['Endividamento Geral (EG)']
        if eg > 0.7:
            st.error("⚠️ Alto nível de endividamento")
        elif eg > 0.5:
            st.warning("⚡ Endividamento moderado")
        else:
            st.success("✅ Endividamento controlado")

def render_ciclo_financeiro(df, financial_analyzer):
    """
    Página especializada em ciclo financeiro
    """
    st.title("⏱️ Análise do Ciclo Operacional e Financeiro")
    st.markdown("---")
    
    # Descrição
    st.markdown("""
    ### 🔄 **Prazos Médios e Ciclos**
    
    - **PMRE**: Prazo Médio de Renovação dos Estoques
    - **PMRV**: Prazo Médio de Recebimento das Vendas
    - **PMPC**: Prazo Médio de Pagamento das Compras
    - **Ciclo Operacional**: PMRE + PMRV
    - **Ciclo Financeiro**: Ciclo Operacional - PMPC
    """)
    
    # Gráfico de ciclo financeiro
    fig = financial_analyzer.create_ciclo_financeiro()
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabela com prazos
    st.subheader("📋 Prazos em Dias")
    ciclo_cols = ['Ano', 'Prazo Médio de Renovação dos Estoques (PMRE) ', 
                  'Prazo Médio de Recebimento das Vendas (PMRV) ',
                  'Prazo Médio de Pagamento das Compras (PMPC) ',
                  'Ciclo Operacional e Ciclo Financeiro']
    df_ciclo = df[ciclo_cols].round(0)
    st.dataframe(df_ciclo, use_container_width=True)

def render_analise_dupont(df, financial_analyzer):
    """
    Página especializada em análise DuPont
    """
    st.title("🔍 Análise DuPont - Decomposição da Rentabilidade")
    st.markdown("---")
    
    # Descrição
    st.markdown("""
    ### 🧮 **Análise DuPont**
    
    **ROA = Margem Líquida × Giro do Ativo**
    
    **ROE = ROA × Multiplicador de Alavancagem Financeira**
    
    Esta análise permite identificar os direcionadores da rentabilidade.
    """)
    
    # Gráfico DuPont
    fig = financial_analyzer.create_analise_dupont()
    st.plotly_chart(fig, use_container_width=True)
    
    # Decomposição atual
    st.subheader("🧮 Decomposição Atual")
    ano_atual = df['Ano'].max()
    dados = df[df['Ano'] == ano_atual].iloc[0]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("� Margem Líquida", f"{dados['Margem Líquida (ML)']:.1%}")
        st.metric("⚙️ Giro do Ativo", f"{dados['Giro do Ativo (GA)']:.2f}")
    
    with col2:
        roa_calculado = dados['Margem Líquida (ML)'] * dados['Giro do Ativo (GA)']
        st.metric("🎯 ROA Calculado", f"{roa_calculado:.1%}")
        st.metric("🎯 ROA Real", f"{dados['Rentabilidade do Ativo (ROA ou ROI)']:.1%}")
    
    with col3:
        st.metric("⚡ Multiplicador", f"{dados['Multiplicador de Alavancagem Financeira (MAF)']:.2f}")
        st.metric("📈 ROE", f"{dados['Rentabilidade do Patrimônio Líquido (ROE) ']:.1%}")

def render_visao_geral(df, financial_analyzer):
    """
    Página com heatmap e visão geral
    """
    st.title("🌡️ Visão Geral - Heatmap de Indicadores")
    st.markdown("---")
    
    # Heatmap de indicadores
    fig = financial_analyzer.create_heatmap_indicadores()
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabela completa
    st.subheader("📋 Dados Completos")
    
    # Mostrar apenas colunas principais para melhor visualização
    colunas_principais = [
        'Ano', 'Ativo Total', 'Receita Líquida', 'Lucro Líquido',
        'Rentabilidade do Ativo (ROA ou ROI)', 'Rentabilidade do Patrimônio Líquido (ROE) ',
        'Liquidez Corrente (LC) ', 'Endividamento Geral (EG)', 'Margem Líquida (ML)'
    ]
    
    df_resumo = df[colunas_principais].round(3)
    st.dataframe(df_resumo, use_container_width=True)
    
    # Exportar dados
    if st.button("� Baixar Dados Completos"):
        csv = df.to_csv(index=False, sep=';', decimal=',')
        st.download_button(
            label="💾 Download CSV",
            data=csv,
            file_name=f"analise_financeira_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    # Inicializar gerenciador de gráficos
    chart_manager = ChartManager()
    
    # Gráfico 1: Evolução temporal
    st.markdown("### 📈 Evolução Temporal")
    fig1 = chart_manager.create_chart_full("evolucao_temporal", df_filtrado)
    if fig1:
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("Dados insuficientes para gerar gráfico de evolução temporal")
    
    # Gráficos 2 e 3 lado a lado
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Top Despesas por Categoria")
        fig2 = chart_manager.create_chart_full("despesas_categoria", df_filtrado)
        if fig2:
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Sem dados de despesas para exibir")
    
    with col2:
        st.markdown("### 🥧 Distribuição de Receitas")
        fig3 = chart_manager.create_chart_full("distribuicao_receitas", df_filtrado)
        if fig3:
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("Sem dados de receitas para exibir")
    
    # Gráficos adicionais
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("### 🥧 Distribuição de Despesas")
        fig4 = chart_manager.create_chart_full("distribuicao_despesas", df_filtrado)
        if fig4:
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("Sem dados de despesas para exibir")
    
    with col4:
        st.markdown("### 📊 Saldo Mensal")
        fig5 = chart_manager.create_chart_full("comparativo_mensal", df_filtrado)
        if fig5:
            st.plotly_chart(fig5, use_container_width=True)
        else:
            st.info("Dados insuficientes para calcular saldo mensal")
    
    # Call-to-action para IA
    st.markdown("---")
    st.info("💡 **Quer análises inteligentes destes gráficos?** Acesse a página **'🤖 Chat com IA'** no menu lateral!")
    
    # Tabela de dados detalhados
    st.markdown("---")
    st.subheader("📋 Dados Detalhados")
    
    if not df_filtrado.empty:
        # Formatar a coluna de data para exibição
        df_exibicao = df_filtrado.copy()
        df_exibicao['Data'] = df_exibicao['Data'].dt.strftime('%d/%m/%Y')
        df_exibicao['Valor'] = df_exibicao['Valor'].apply(lambda x: f"R$ {x:,.2f}")
        
        st.dataframe(
            df_exibicao,
            use_container_width=True,
            hide_index=True
        )
        
        st.caption(f"Total de registros: {len(df_filtrado)}")
    else:
        st.info("Nenhum dado encontrado para os filtros selecionados.")

def render_ai_chat_page():
    """
    Renderiza a página de chat com IA - NOVA FUNCIONALIDADE PRINCIPAL
    """
    st.title("🤖 Chat com IA - Análise Inteligente")
    st.markdown("Converse com a IA sobre seus dados contábeis e obtenha insights sobre gráficos específicos")
    st.markdown("---")
    
    # Verificar se há dados disponíveis
    if 'df_filtrado' not in st.session_state:
        st.warning("⚠️ **Dados não disponíveis!** Visite primeiro a página 'Dashboard Principal' para carregar os dados.")
        st.stop()
    
    df_filtrado = st.session_state.df_filtrado
    kpis = st.session_state.get('kpis', {})
    
    # Inicializar IA e gerenciador de gráficos
    analyzer = AIAnalyzer()
    chart_manager = ChartManager()
    
    if not analyzer.is_available():
        st.error("❌ **API do Google Gemini não configurada!**")
        st.info("""
        Para usar a análise de IA:
        1. Obtenha uma API key em: https://makersuite.google.com/app/apikey
        2. Crie um arquivo `.env` na raiz do projeto
        3. Adicione: `GOOGLE_GEMINI_API_KEY=sua_chave_aqui`
        """)
        st.stop()
    
    # === SEÇÃO 1: SELETOR DE GRÁFICOS ===
    st.subheader("📊 Selecione um Gráfico para Análise")
    
    # Dropdown com gráficos disponíveis
    chart_options = ["🎯 Análise Geral dos Dados"] + chart_manager.get_available_charts()
    
    selected_chart_display = st.selectbox(
        "Escolha um gráfico ou análise geral:",
        chart_options,
        index=0,
        help="Selecione um gráfico específico para receber análises focadas da IA"
    )
    
    # === SEÇÃO 2: PREVIEW DO GRÁFICO SELECIONADO ===
    selected_chart_key = None
    
    if selected_chart_display != "🎯 Análise Geral dos Dados":
        selected_chart_key = chart_manager.get_chart_key_from_display(selected_chart_display)
        
        if selected_chart_key:
            st.markdown("### 👁️ Preview do Gráfico Selecionado")
            
            # Container para preview
            with st.container():
                col1, col2, col3 = st.columns([1, 2, 1])
                
                with col2:
                    # Criar miniatura do gráfico
                    thumbnail_fig = chart_manager.create_chart_thumbnail(
                        selected_chart_key, 
                        df_filtrado,
                        container_width=400,
                        container_height=250
                    )
                    
                    if thumbnail_fig:
                        st.plotly_chart(thumbnail_fig, use_container_width=True)
                        
                        # Informações do gráfico
                        chart_info = chart_manager.get_chart_info(selected_chart_key)
                        st.caption(f"📋 {chart_info.get('description', 'Gráfico selecionado')}")
                    else:
                        st.info("📊 Dados insuficientes para gerar este gráfico")
    
    st.markdown("---")
    
    # === SEÇÃO 3: INTERFACE DE CHAT ===
    st.subheader("💬 Conversa com a IA")
    
    # Inicializar histórico de chat no session_state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Campo de input para pergunta
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_question = st.text_area(
            "Digite sua pergunta:",
            placeholder="Ex: Quais são os principais insights deste gráfico? Como posso otimizar estes dados?",
            height=100,
            key="user_input"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 **Enviar**", type="primary", use_container_width=True):
            if user_question.strip():
                # Adicionar pergunta ao histórico
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                # Preparar contexto baseado na seleção
                if selected_chart_key:
                    chart_data = chart_manager.get_chart_data_for_ai(selected_chart_key, df_filtrado)
                    chart_info = chart_manager.get_chart_info(selected_chart_key)
                    context = f"Analisando especificamente o gráfico: {chart_info['name']}"
                else:
                    chart_data = df_filtrado
                    context = "Análise geral dos dados contábeis"
                
                # Mostrar animação de carregamento
                with st.spinner(f"🤖 IA analisando: {context}..."):
                    # Animação de progresso
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i in range(100):
                        if i < 30:
                            status_text.info("🔍 Analisando sua pergunta...")
                        elif i < 60:
                            status_text.info("📊 Processando dados do gráfico...")
                        elif i < 85:
                            status_text.info("🤖 IA formulando resposta...")
                        else:
                            status_text.info("✨ Finalizando análise...")
                        
                        progress_bar.progress(i + 1)
                        time.sleep(0.025)  # 2.5 segundos total
                    
                    # Gerar resposta da IA
                    try:
                        if selected_chart_key:
                            # Análise focada no gráfico específico
                            ai_response = analyzer.generate_chart_insights(
                                chart_data.to_dict('records') if hasattr(chart_data, 'to_dict') else chart_data,
                                selected_chart_key,
                                custom_question=user_question
                            )
                        else:
                            # Análise geral
                            ai_response = analyzer.generate_insights(
                                st.session_state.df_original,
                                df_filtrado,
                                kpis,
                                custom_question=user_question
                            )
                    except Exception as e:
                        ai_response = f"❌ Erro ao gerar resposta: {str(e)}"
                    
                    # Limpar animação
                    progress_bar.empty()
                    status_text.empty()
                
                # Adicionar conversa ao histórico
                st.session_state.chat_history.append({
                    'timestamp': timestamp,
                    'user_question': user_question,
                    'ai_response': ai_response,
                    'context': context,
                    'chart_key': selected_chart_key
                })
                
                # Limpar campo de input
                st.rerun()
    
    # === SEÇÃO 4: HISTÓRICO DE CONVERSAS ===
    if st.session_state.chat_history:
        st.markdown("---")
        st.subheader("💬 Histórico de Conversas")
        
        # Botão para limpar histórico
        if st.button("🗑️ Limpar Histórico", help="Remove todas as conversas anteriores"):
            st.session_state.chat_history = []
            st.rerun()
        
        # Exibir conversas (mais recente primeiro)
        for i, chat in enumerate(reversed(st.session_state.chat_history)):
            with st.expander(f"💬 Conversa {len(st.session_state.chat_history) - i} - {chat['timestamp']} | {chat['context']}", expanded=(i == 0)):
                # Pergunta do usuário
                st.markdown("**👤 Sua pergunta:**")
                st.markdown(f"*{chat['user_question']}*")
                
                st.markdown("---")
                
                # Resposta da IA
                st.markdown("**🤖 Resposta da IA:**")
                st.markdown(chat['ai_response'])
                
                # Mostrar miniatura do gráfico se foi análise específica
                if chat['chart_key']:
                    st.markdown("**📊 Gráfico analisado:**")
                    mini_fig = chart_manager.create_chart_thumbnail(
                        chat['chart_key'], 
                        df_filtrado,
                        container_width=300,
                        container_height=200
                    )
                    if mini_fig:
                        st.plotly_chart(mini_fig, use_container_width=True)
    
    # === SEÇÃO 5: SUGESTÕES DE PERGUNTAS ===
    if not st.session_state.chat_history:
        st.markdown("---")
        st.subheader("💡 Sugestões de Perguntas")
        
        suggestions = [
            "Quais são os principais insights financeiros dos dados atuais?",
            "Como posso reduzir as despesas sem impactar a operação?",
            "Quais categorias de receita têm maior potencial de crescimento?",
            "Há alguma tendência preocupante nos dados?",
            "Qual é a sazonalidade dos nossos resultados?",
            "Como nossa performance se compara aos meses anteriores?"
        ]
        
        cols = st.columns(2)
        for i, suggestion in enumerate(suggestions):
            with cols[i % 2]:
                if st.button(f"❓ {suggestion}", key=f"suggestion_{i}", use_container_width=True):
                    st.session_state.user_input = suggestion
                    st.rerun()

def render_settings_page():
    """
    Renderiza a página de configurações
    """
    st.title("⚙️ Configurações")
    st.markdown("Configure as preferências do dashboard e da IA")
    st.markdown("---")
    
    # Seção API do Gemini
    st.subheader("🤖 Configuração da API Google Gemini")
    
    analyzer = AIAnalyzer()
    if analyzer.is_available():
        st.success("✅ **API configurada corretamente!**")
        st.info("A IA está pronta para uso nas análises do dashboard.")
    else:
        st.error("❌ **API não configurada**")
        st.markdown("""
        **Para configurar a API:**
        1. Obtenha sua API key em: https://makersuite.google.com/app/apikey
        2. Crie um arquivo `.env` na raiz do projeto
        3. Adicione: `GOOGLE_GEMINI_API_KEY=sua_chave_aqui`
        4. Reinicie o aplicativo
        """)
    
    st.markdown("---")
    
    # Informações do projeto
    st.subheader("ℹ️ Informações do Projeto")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📊 Dashboard de Análise Contábil**
        - Versão: 2.0
        - Framework: Streamlit
        - IA: Google Gemini
        """)
    
    with col2:
        st.markdown("""
        **🚀 Funcionalidades:**
        - Análises gráficas interativas
        - Chat inteligente com IA
        - Filtros dinâmicos
        - Múltiplas visualizações
        """)
    
    # Botão para recarregar dados
    st.markdown("---")
    st.subheader("🔄 Gerenciamento de Dados")
    
    if st.button("🔄 Recarregar Dados Fictícios", type="secondary"):
        st.session_state.df_original = gerar_dados_contabeis()
        st.success("✅ Dados recarregados com sucesso!")
        st.rerun()
    
    # Estatísticas dos dados atuais
    if 'df_original' in st.session_state:
        df = st.session_state.df_original
        st.markdown("**📈 Estatísticas Atuais:**")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Registros", len(df))
        
        with col2:
            st.metric("Período", f"{df['Data'].min().strftime('%m/%Y')} - {df['Data'].max().strftime('%m/%Y')}")
        
        with col3:
            st.metric("Categorias", len(df['Categoria'].unique()))
        
        with col4:
            receitas = len(df[df['Tipo'] == 'Receita'])
            despesas = len(df[df['Tipo'] == 'Despesa'])
            st.metric("Receitas/Despesas", f"{receitas}/{despesas}")

def render_ai_chat_page_financial(df, financial_analyzer):
    """
    Página do Chat com IA especializada para dados financeiros
    """
    st.title("🤖 Chat com IA - Análise Financeira")
    st.markdown("Converse com nossa IA sobre os indicadores financeiros da empresa")
    st.markdown("---")
    
    # Layout em duas colunas principais
    col_main, col_sidebar = st.columns([2, 1])
    
    with col_sidebar:
        st.subheader("📊 Análises Disponíveis")
        
        opcoes_analise = {
            "📈 Análise de Rentabilidade": "rentabilidade",
            "🛡️ Análise de Liquidez": "liquidez", 
            "🏦 Estrutura de Capital": "capital",
            "⏱️ Ciclo Financeiro": "ciclo",
            "🔍 Análise DuPont": "dupont",
            "🌡️ Visão Geral": "geral"
        }
        
        analise_selecionada = st.selectbox(
            "Escolha o tipo de análise:",
            list(opcoes_analise.keys()),
            key="analise_selector"
        )
        
        # Preview melhorado do gráfico
        st.markdown("### 🔍 Preview")
        tipo_analise = opcoes_analise[analise_selecionada]
        
        try:
            if tipo_analise == "rentabilidade":
                fig_mini = financial_analyzer.create_rentabilidade_chart()
            elif tipo_analise == "liquidez":
                fig_mini = financial_analyzer.create_liquidez_radar()
            elif tipo_analise == "capital":
                fig_mini = financial_analyzer.create_estrutura_capital()
            elif tipo_analise == "ciclo":
                fig_mini = financial_analyzer.create_ciclo_financeiro()
            elif tipo_analise == "dupont":
                fig_mini = financial_analyzer.create_analise_dupont()
            else:
                fig_mini = financial_analyzer.create_heatmap_indicadores()
            
            # Configuração melhorada para preview
            fig_mini.update_layout(
                height=300, 
                showlegend=True,
                title="",
                margin=dict(l=10, r=10, t=20, b=10),
                font=dict(size=10)
            )
            st.plotly_chart(fig_mini, use_container_width=True, key=f"preview_{tipo_analise}")
            
        except Exception as e:
            st.info("📊 Preview do gráfico será exibido aqui")
            
        # Sugestões de perguntas na sidebar
        st.markdown("### 💡 Sugestões")
        sugestoes = [
            "Analise a evolução da rentabilidade",
            "Quais os riscos de liquidez?", 
            "A estrutura de capital é adequada?",
            "Como melhorar o ciclo financeiro?",
            "Principais pontos de atenção",
            "Compare os anos analisados"
        ]
        
        for i, sugestao in enumerate(sugestoes):
            if st.button(f"💭 {sugestao}", key=f"sug_{i}", use_container_width=True):
                st.session_state.pergunta_sugerida = sugestao
    
    with col_main:
        # Inicializar histórico da conversa
        if 'financial_chat_history' not in st.session_state:
            st.session_state.financial_chat_history = []
        
        # Inicializar AI Analyzer
        if 'financial_ai_analyzer' not in st.session_state:
            st.session_state.financial_ai_analyzer = AIAnalyzer()
        
        # Interface de chat melhorada
        st.subheader("💬 Chat com IA Financeira")
        
        # Input para nova pergunta
        pergunta_default = st.session_state.get('pergunta_sugerida', '')
        pergunta = st.text_area(
            "Faça sua pergunta sobre os dados financeiros:",
            value=pergunta_default,
            placeholder="Ex: Como está a evolução da rentabilidade? Quais são os principais riscos de liquidez?",
            height=100,
            key="pergunta_input"
        )
        
        # Limpar sugestão após usar
        if 'pergunta_sugerida' in st.session_state:
            del st.session_state.pergunta_sugerida
        
        # Botões de ação
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        
        with col_btn1:
            analisar_clicked = st.button("🚀 Analisar", type="primary", use_container_width=True)
        
        with col_btn2:
            if st.button("🗑️ Limpar Histórico", use_container_width=True):
                st.session_state.financial_chat_history = []
                st.success("🗑️ Histórico limpo!")
                st.rerun()
        
        # Processamento da pergunta
        if analisar_clicked and pergunta:
            with st.spinner("🤖 IA analisando os dados financeiros..."):
                try:
                    # Preparar dados para IA
                    dados_para_ia = financial_analyzer.get_data_for_ai()
                    
                    # Gerar resposta
                    resposta = st.session_state.financial_ai_analyzer.generate_chart_insights(
                        dados_para_ia,
                        f"Análise financeira especializada sobre {analise_selecionada.lower()}: {pergunta}"
                    )
                    
                    # Adicionar ao histórico
                    st.session_state.financial_chat_history.append((pergunta, resposta, analise_selecionada))
                    
                    st.success("✅ Análise concluída!")
                    
                except Exception as e:
                    st.error(f"❌ Erro ao analisar: {str(e)}")
        
        elif analisar_clicked and not pergunta:
            st.warning("⚠️ Por favor, digite uma pergunta.")
        
        # Exibição do histórico melhorada
        if st.session_state.financial_chat_history:
            st.markdown("---")
            st.subheader("� Histórico da Conversa")
            
            # Exibir conversas mais recentes primeiro
            for i, (pergunta_hist, resposta_hist, analise_tipo) in enumerate(reversed(st.session_state.financial_chat_history)):
                with st.container():
                    # Header da conversa
                    st.markdown(f"""
                    <div style="
                        background-color: #f0f2f6; 
                        padding: 10px; 
                        border-radius: 10px; 
                        margin: 10px 0;
                        border-left: 4px solid #1f77b4;
                    ">
                        <strong>💭 Pergunta {len(st.session_state.financial_chat_history) - i}:</strong> {analise_tipo}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Pergunta
                    st.markdown(f"**🙋‍♂️ Pergunta:** {pergunta_hist}")
                    
                    # Resposta formatada
                    st.markdown("**🤖 Resposta da IA:**")
                    
                    # Container para resposta com estilo
                    with st.container():
                        # Dividir resposta em parágrafos
                        paragrafos = resposta_hist.split('\n\n')
                        
                        for paragrafo in paragrafos:
                            if paragrafo.strip():
                                # Verificar se é um título (contém **)
                                if '**' in paragrafo:
                                    st.markdown(paragrafo)
                                else:
                                    # Texto normal com melhor espaçamento
                                    st.markdown(f"""
                                    <div style="
                                        background-color: #ffffff; 
                                        padding: 15px; 
                                        border-radius: 8px; 
                                        margin: 5px 0;
                                        border: 1px solid #e0e0e0;
                                        line-height: 1.6;
                                    ">
                                        {paragrafo}
                                    </div>
                                    """, unsafe_allow_html=True)
                    
                    st.markdown("---")

# Executar a aplicação
if __name__ == "__main__":
    main()
