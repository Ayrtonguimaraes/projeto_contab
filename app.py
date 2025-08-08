"""
Aplicação Principal - Dashboard de Análise Financeira Corporativa
Restauração completa após corrupção do arquivo.
(Fase 1 UX: Filtros avançados, KPIs com variação, export & contexto)
"""

import streamlit as st
from config.settings import AppConfig
from utils.data_loader import carregar_dados
from financial_analyzer import FinancialAnalyzer
from pages.page_manager import PageManager
from datetime import datetime

# --------------------------------------------------
# Configuração inicial da página
# --------------------------------------------------
AppConfig.configure_page()

# Oculta navegação multipage nativa do Streamlit (links automáticos da pasta 'pages')
# para evitar duplicidade/confusão com nossa navegação customizada.
def _hide_native_multipage_nav():
    st.markdown(
        """
        <style>
        /* Esconde bloco padrão de navegação automática */
        [data-testid="stSidebarNav"] {display: none !important;}
        /* Remove espaço extra deixado pelo bloco oculto */
        section[data-testid="stSidebar"] div:first-child {padding-top: 0.5rem;}
        </style>
        """,
        unsafe_allow_html=True
    )

_hide_native_multipage_nav()

# --------------------------------------------------
# Funções de UI (Sidebar, utilitários)
# --------------------------------------------------

def format_currency(value):
    try:
        return f"R$ {float(value):,.0f}".replace(',', '.').replace('.00', '')
    except Exception:
        return str(value)


def format_percentage(value):
    try:
        return f"{float(value):.1%}"
    except Exception:
        return str(value)


def _calc_delta(atual, anterior):
    try:
        if anterior in (0, None):
            return "—"
        return f"{((atual - anterior)/anterior)*100:.1f}%"
    except Exception:
        return "—"


def criar_sidebar(df, analyzer):
    """Cria sidebar apenas com filtros, resumo e exportação (sem KPIs)."""
    st.sidebar.title("🏢 Análise Financeira")
    # Toggle modo simplificado (afeta páginas de gráficos)
    st.sidebar.checkbox(
        "Modo simplificado de gráficos",
        key="modo_simplificado",
        help="Exibe versões resumidas (tabelas/deltas) quando disponível para poucos anos"
    )

    if df is None or df.empty:
        st.sidebar.error("❌ Nenhum dado disponível")
        return df, []

    # Filtros
    with st.sidebar.expander("🎛️ Filtros", expanded=True):
        anos_disponiveis = sorted(df['Ano'].unique(), reverse=True) if 'Ano' in df.columns else []
        anos_sel = st.multiselect(
            "Anos", anos_disponiveis,
            default=anos_disponiveis[:2] if len(anos_disponiveis) >= 2 else anos_disponiveis
        )
        if not anos_sel:
            st.info("Selecione ao menos um ano.")
        if st.button("🔄 Reset Filtros"):
            st.session_state.pop('anos_sel', None)
            st.rerun()

    # Filtragem por ano
    if anos_sel:
        df_filtrado = df[df['Ano'].isin(anos_sel)].copy()
    else:
        df_filtrado = df.copy()

    # Resumo filtros
    st.sidebar.markdown("---")
    st.sidebar.caption(
        f"🧾 Registros: {len(df_filtrado)} | Anos: {', '.join(map(str, sorted(df_filtrado['Ano'].unique())))}"
    )

    # Exportação
    try:
        csv_data = df_filtrado.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button(
            "💾 Exportar CSV", csv_data, file_name="dados_financeiros.csv", mime="text/csv"
        )
    except Exception:
        pass

    return df_filtrado, anos_sel

# --------------------------------------------------
# Função Principal
# --------------------------------------------------

def main():
    # Carregar dados base (uma vez)
    if 'df_original' not in st.session_state:
        try:
            df = carregar_dados()
            st.session_state.df_original = df
            st.session_state.financial_analyzer = FinancialAnalyzer(df.copy())
            st.session_state.last_update = datetime.now()
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")
            st.stop()

    df = st.session_state.df_original
    base_analyzer = st.session_state.financial_analyzer

    # Navegação
    st.sidebar.title("🧭 Navegação")
    paginas = AppConfig.NAVIGATION
    label_selecionada = st.sidebar.radio("Selecione a análise:", list(paginas.keys()))
    page_key = paginas[label_selecionada]

    # Sidebar (retorna df filtrado e anos)
    df_filtrado, anos_sel = criar_sidebar(df, base_analyzer)

    # Analyzer filtrado (sem perder original) para páginas
    if 'Ano' in df_filtrado.columns and 0 < len(df_filtrado['Ano'].unique()) < len(df['Ano'].unique()):
        analyzer_page = FinancialAnalyzer(df_filtrado.copy())
    else:
        analyzer_page = base_analyzer

    # Header global (contexto)
    st.markdown(f"### 📌 Contexto Atual")
    st.caption(
        f"Anos Selecionados: {', '.join(map(str, anos_sel)) if anos_sel else 'Todos'} | "
        f"Atualizado em: {st.session_state.get('last_update').strftime('%d/%m/%Y %H:%M')}"
    )
    st.markdown("---")

    # Renderização
    manager = PageManager()
    manager.render_page(page_key, df_filtrado if analyzer_page != base_analyzer else df, analyzer_page)

# --------------------------------------------------
# Execução
# --------------------------------------------------
if __name__ == "__main__":
    main()
