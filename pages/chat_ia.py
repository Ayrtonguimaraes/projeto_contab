"""
Página de Chat com IA
Refatorada: centraliza seleção de gráfico (dropdown + mini preview) e integra chat contextual.
"""

import streamlit as st
from pages.base_page import BasePage
from ai_analyzer import AIAnalyzer
from datetime import datetime
import pandas as pd  # pode ser útil para checagens

# Tipos de gráficos / visões suportados pelo FinancialAnalyzer
_FINANCIAL_CHART_DEFS = [
    {
        "id": "rentabilidade",
        "label": "📈 Rentabilidade (ROE / ROA / Margem)",
        "builder": "create_rentabilidade_chart",
        "description": "Evolução de ROE, ROA e Margem Líquida" ,
    },
    {
        "id": "liquidez",
        "label": "🛡️ Liquidez (Radar)",
        "builder": "create_liquidez_radar",
        "description": "Radar dos indicadores de liquidez (LG, LC, LS, LI)",
    },
    {
        "id": "capital",
        "label": "🏦 Estrutura de Capital",
        "builder": "create_estrutura_capital",
        "description": "Endividamento, composição e evolução da estrutura de capital",
    },
    {
        "id": "ciclo",
        "label": "⏱️ Ciclo Financeiro",
        "builder": "create_ciclo_financeiro",
        "description": "Prazos médios e comparação de ciclos operacional x financeiro",
    },
    {
        "id": "dupont",
        "label": "🔍 Análise DuPont",
        "builder": "create_analise_dupont",
        "description": "Decomposição da rentabilidade (Margem × Giro × Alavancagem)",
    },
    {
        "id": "evolucao_patrimonial",
        "label": "💰 Evolução Patrimonial",
        "builder": "create_evolucao_patrimonial",
        "description": "Evolução do Ativo, PL e Passivos ao longo do tempo",
    },
    {
        "id": "indicadores",
        "label": "📋 Indicadores Gerais (Tabela Consolidada)",
        "builder": "get_indicadores_tabela",
        "description": "Tabela consolidada de indicadores e variações ano a ano",
    },
]

class ChatIAPage(BasePage):
    """Página de chat com IA contextual a um gráfico selecionado"""
    
    def __init__(self, df, financial_analyzer):
        super().__init__(df, financial_analyzer)
        self.ai_analyzer = AIAnalyzer()
        # Inicializa registro de gráficos / visões
        self.chart_registry = self._build_chart_registry()
    
    # --------------------------------------------------
    # Registro / Preparação de Gráficos
    # --------------------------------------------------
    def _build_chart_registry(self):
        registry = {}
        for meta in _FINANCIAL_CHART_DEFS:
            fn_name = meta["builder"]
            if hasattr(self.analyzer, fn_name):  # garantir existência
                registry[meta["id"]] = {
                    "label": meta["label"],
                    "description": meta["description"],
                    "builder": getattr(self.analyzer, fn_name)
                }
        return registry
    
    def _get_chart_options(self):
        return [c["label"] for c in (self.chart_registry[id] | {"id": id} for id in self.chart_registry)]
    
    def _resolve_chart_id(self, label):
        for cid, meta in self.chart_registry.items():
            if meta["label"] == label:
                return cid
        return None
    
    # --------------------------------------------------
    # Render Principal
    # --------------------------------------------------
    def render(self):
        st.title("🤖 Chat com IA - Análise de Gráficos / Indicadores")
        st.caption("Selecione uma visualização (gráfico ou tabela), veja a miniatura e faça perguntas. A IA responderá contextualizada à visão escolhida.")
        st.markdown("---")
        
        if not self.ai_analyzer.is_available():
            st.error("API Gemini não configurada.")
            return
        
        self._render_chart_selector()
        self._render_chat_interface()
        self.render_sidebar_info()
    
    # --------------------------------------------------
    # Seleção e Miniatura
    # --------------------------------------------------
    def _render_chart_selector(self):
        st.subheader("1️⃣ Seleção da Visualização")
        col_sel, col_prev = st.columns([1.2, 1])
        with col_sel:
            options = self._get_chart_options()
            if not options:
                st.warning("Nenhuma visualização disponível.")
                return
            selected_label = st.selectbox(
                "Selecione para análise:",
                options,
                key="ai_chart_select"
            )
            chart_id = self._resolve_chart_id(selected_label)
            st.session_state.selected_chart_id = chart_id
            meta = self.chart_registry.get(chart_id, {})
            st.caption(meta.get("description", ""))
        with col_prev:
            self._render_chart_thumbnail()
        st.markdown("---")
    
    def _render_chart_thumbnail(self):
        chart_id = st.session_state.get('selected_chart_id')
        if not chart_id:
            st.info("Miniatura aparecerá aqui.")
            return
        meta = self.chart_registry.get(chart_id)
        if not meta:
            st.warning("Visualização não encontrada.")
            return
        try:
            obj = meta["builder"]()
            st.markdown("**Miniatura**")
            # Caso especial: tabela de indicadores
            if chart_id == "indicadores":
                if isinstance(obj, pd.DataFrame) and not obj.empty:
                    # Mostrar apenas algumas colunas principais para miniatura
                    cols_show = [c for c in ['Indicador','Categoria','Ano Anterior','Ano Atual','Variação %'] if c in obj.columns]
                    st.dataframe(obj[cols_show].head(15), use_container_width=True)
                else:
                    st.info("Tabela de indicadores vazia ou indisponível.")
            else:
                # Assumir Plotly Figure
                if hasattr(obj, 'update_layout'):
                    obj.update_layout(height=300, margin=dict(l=10, r=10, t=30, b=10), title=dict(text="", font=dict(size=12)))
                st.plotly_chart(obj, use_container_width=True)
        except Exception as e:
            st.warning(f"Não foi possível gerar miniatura: {e}")
    
    # --------------------------------------------------
    # Preparação de Dados para IA (por visualização)
    # --------------------------------------------------
    def _prepare_chart_data(self, chart_id):
        df = self.df
        data = {"erro": "visualização não suportada"}
        try:
            if chart_id == "rentabilidade":
                cols = [
                    'Ano', 'Rentabilidade do Patrimônio Líquido (ROE) ',
                    'Rentabilidade do Ativo (ROA ou ROI)', 'Margem Líquida (ML)'
                ]
                data = df[cols].to_dict('records') if all(c in df.columns for c in cols) else {"erro": "colunas ausentes"}
            elif chart_id == "liquidez":
                cols = ['Ano','Liquidez Geral (LG)','Liquidez Corrente (LC) ','Liquidez Seca (LS)','Liquidez Imediata (LI)']
                data = df[cols].to_dict('records') if all(c in df.columns for c in cols) else {"erro": "colunas ausentes"}
            elif chart_id == "capital":
                cols = ['Ano','Endividamento Geral (EG)','Composição do Endividamento (CE)','Participação de Capitais de Terceiros (PCT) – Grau de Endividamento']
                data = df[cols].to_dict('records') if all(c in df.columns for c in cols) else {"erro":"colunas ausentes"}
            elif chart_id == "ciclo":
                cols = ['Ano','Prazo Médio de Renovação dos Estoques (PMRE) ','Prazo Médio de Recebimento das Vendas (PMRV) ','Prazo Médio de Pagamento das Compras (PMPC) ','Ciclo Operacional e Ciclo Financeiro']
                data = df[cols].to_dict('records') if all(c in df.columns for c in cols) else {"erro":"colunas ausentes"}
            elif chart_id == "dupont":
                cols = ['Ano','Margem Líquida (ML)','Giro do Ativo (GA)','Multiplicador de Alavancagem Financeira (MAF)','Rentabilidade do Patrimônio Líquido (ROE) '] 
                data = df[cols].to_dict('records') if all(c in df.columns for c in cols) else {"erro":"colunas ausentes"}
            elif chart_id == "evolucao_patrimonial":
                cols = ['Ano','Ativo Total','Patrimônio Líquido','Passivo Circulante','Passivo Não Circulante']
                data = df[cols].to_dict('records') if all(c in df.columns for c in cols) else {"erro":"colunas ausentes"}
            elif chart_id == "indicadores":
                tabela = self.analyzer.get_indicadores_tabela()
                if isinstance(tabela, pd.DataFrame) and not tabela.empty:
                    data = tabela.to_dict('records')
                else:
                    data = {"erro": "tabela de indicadores indisponível"}
        except Exception as e:
            data = {"erro": f"falha ao preparar dados: {e}"}
        return data
    
    # --------------------------------------------------
    # Chat
    # --------------------------------------------------
    def _init_chat_state(self):
        if 'ai_graph_chat_history' not in st.session_state:
            st.session_state.ai_graph_chat_history = []
    
    def _render_chat_interface(self):
        self._init_chat_state()
        st.subheader("2️⃣ Pergunte à IA sobre a Visualização")
        chart_id = st.session_state.get('selected_chart_id')
        if not chart_id:
            st.info("Selecione algo primeiro.")
            return
        
        placeholder_ex = "Ex: Quais destaques? Maiores variações? Riscos de liquidez?" if chart_id == 'indicadores' else "Ex: Como evoluiu o ROE? Quais riscos de liquidez aparecem?"
        pergunta = st.text_area(
            "Sua pergunta:",
            placeholder=placeholder_ex,
            key="ai_chart_question",
            height=110
        )
        col_a, col_b, col_c = st.columns([1,1,1])
        with col_a:
            analisar = st.button("🚀 Analisar", type="primary")
        with col_b:
            if st.button("🧹 Limpar Histórico"):
                st.session_state.ai_graph_chat_history = []
                st.success("Histórico limpo")
                st.rerun()
        with col_c:
            st.download_button(
                "⬇️ Exportar Histórico",
                data=self._export_history_to_markdown(),
                file_name="chat_ia_graficos.md",
                mime="text/markdown",
                disabled=not st.session_state.ai_graph_chat_history
            )
        
        if analisar:
            if not pergunta.strip():
                st.warning("Digite uma pergunta.")
            else:
                with st.spinner("IA analisando..."):
                    chart_data = self._prepare_chart_data(chart_id)
                    resposta = self.ai_analyzer.generate_chart_insights(
                        chart_data=chart_data,
                        chart_type=chart_id,
                        df_filtrado=self.df,
                        custom_question=pergunta
                    )
                    st.session_state.ai_graph_chat_history.append({
                        "chart_id": chart_id,
                        "chart_label": self.chart_registry[chart_id]["label"],
                        "pergunta": pergunta,
                        "resposta": resposta,
                        "ts": datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                    })
                    st.success("Análise concluída")
        
        self._render_history()
    
    def _render_history(self):
        if not st.session_state.ai_graph_chat_history:
            return
        st.markdown("---")
        st.subheader("💬 Histórico")
        for item in reversed(st.session_state.ai_graph_chat_history):
            with st.expander(f"{item['ts']} • {item['chart_label']}"):
                st.markdown(f"**Pergunta:** {item['pergunta']}")
                st.markdown("**Resposta da IA:**")
                st.markdown(item['resposta'])
    
    def _export_history_to_markdown(self):
        lines = ["# Histórico Chat IA (Gráficos / Indicadores)\n"]
        for item in st.session_state.ai_graph_chat_history:
            lines.append(f"## {item['ts']} - {item['chart_label']}")
            lines.append(f"**Pergunta:** {item['pergunta']}")
            lines.append("**Resposta:**")
            lines.append(item['resposta'])
            lines.append("\n---\n")
        return "\n".join(lines)
