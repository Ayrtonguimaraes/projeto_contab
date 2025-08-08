"""
Página de Chat com IA
Refatorada: centraliza seleção de gráfico (dropdown + mini preview) e integra chat contextual.
"""

import streamlit as st
from pages.base_page import BasePage
from ai_analyzer import AIAnalyzer
from datetime import datetime
import pandas as pd  # pode ser útil para checagens

# Métricas disponíveis na base de dados (baseado nas colunas do CSV)
_METRICAS_FINANCEIRAS = [
    # === ESTRUTURA PATRIMONIAL ===
    {
        "categoria": "Estrutura Patrimonial",
        "metricas": [
            {"id": "ativo_total", "nome": "Ativo Total", "coluna": "Ativo Total"},
            {"id": "imobilizado", "nome": "Imobilizado", "coluna": "Imobilizado"},
            {"id": "patrimonio_liquido", "nome": "Patrimônio Líquido", "coluna": "Patrimônio Líquido"},
            {"id": "passivo_circulante", "nome": "Passivo Circulante", "coluna": "Passivo Circulante"},
            {"id": "passivo_nao_circulante", "nome": "Passivo Não Circulante", "coluna": "Passivo Não Circulante"},
            {"id": "realizavel_longo_prazo", "nome": "Realizável a Longo Prazo", "coluna": "Realizável a Longo Prazo"},
        ]
    },
    # === RESULTADO E PERFORMANCE ===
    {
        "categoria": "Resultado e Performance", 
        "metricas": [
            {"id": "receita_liquida", "nome": "Receita Líquida", "coluna": "Receita Líquida"},
            {"id": "lucro_liquido", "nome": "Lucro Líquido", "coluna": "Lucro Líquido"},
            {"id": "lucro_operacional", "nome": "Lucro Operacional", "coluna": "Lucro Operacional"},
            {"id": "lucro_antes_impostos", "nome": "Lucro Antes dos Impostos", "coluna": "Lucro Antes dos Impostos"},
            {"id": "cpv", "nome": "Custo dos Produtos Vendidos (CPV)", "coluna": "Custo dos Produtos Vendidos (CPV)"},
        ]
    },
    # === RENTABILIDADE ===
    {
        "categoria": "Rentabilidade",
        "metricas": [
            {"id": "roe", "nome": "ROE - Rentabilidade do Patrimônio Líquido", "coluna": "Rentabilidade do Patrimônio Líquido (ROE) "},
            {"id": "roa", "nome": "ROA - Rentabilidade do Ativo", "coluna": "Rentabilidade do Ativo (ROA ou ROI)"},
            {"id": "margem_liquida", "nome": "Margem Líquida", "coluna": "Margem Líquida (ML)"},
            {"id": "giro_ativo", "nome": "Giro do Ativo", "coluna": "Giro do Ativo (GA)"},
            {"id": "maf", "nome": "Multiplicador de Alavancagem Financeira", "coluna": "Multiplicador de Alavancagem Financeira (MAF)"},
            {"id": "analise_dupont", "nome": "Análise ROI (Método DuPont)", "coluna": "Análise do ROI (Método DuPont) "},
        ]
    },
    # === LIQUIDEZ ===
    {
        "categoria": "Liquidez",
        "metricas": [
            {"id": "liquidez_corrente", "nome": "Liquidez Corrente", "coluna": "Liquidez Corrente (LC) "},
            {"id": "liquidez_imediata", "nome": "Liquidez Imediata", "coluna": "Liquidez Imediata (LI)"},
            {"id": "liquidez_seca", "nome": "Liquidez Seca", "coluna": "Liquidez Seca (LS)"},
            {"id": "liquidez_geral", "nome": "Liquidez Geral", "coluna": "Liquidez Geral (LG)"},
            {"id": "caixa", "nome": "Caixa e Equivalentes", "coluna": "Caixa e Equivalentes de Caixa"},
        ]
    },
    # === ENDIVIDAMENTO ===
    {
        "categoria": "Endividamento",
        "metricas": [
            {"id": "endividamento_geral", "nome": "Endividamento Geral", "coluna": "Endividamento Geral (EG)"},
            {"id": "pct", "nome": "Participação de Capitais de Terceiros", "coluna": "Participação de Capitais de Terceiros (PCT) – Grau de Endividamento"},
            {"id": "composicao_endividamento", "nome": "Composição do Endividamento", "coluna": "Composição do Endividamento (CE)"},
            {"id": "imobilizacao_pl", "nome": "Grau de Imobilização do PL", "coluna": "Grau de Imobilização do Patrimônio Líquido (ImPL)"},
            {"id": "imobilizacao_rnc", "nome": "Grau de Imobilização dos Recursos não Correntes", "coluna": "Grau de Imobilização dos Recursos não Correntes (IRNC) "},
        ]
    },
    # === CICLOS E PRAZOS ===
    {
        "categoria": "Ciclos e Prazos",
        "metricas": [
            {"id": "pmre", "nome": "Prazo Médio de Renovação dos Estoques", "coluna": "Prazo Médio de Renovação dos Estoques (PMRE) "},
            {"id": "pmrv", "nome": "Prazo Médio de Recebimento das Vendas", "coluna": "Prazo Médio de Recebimento das Vendas (PMRV) "},
            {"id": "pmpc", "nome": "Prazo Médio de Pagamento das Compras", "coluna": "Prazo Médio de Pagamento das Compras (PMPC) "},
            {"id": "ciclo_financeiro", "nome": "Ciclo Operacional e Ciclo Financeiro", "coluna": "Ciclo Operacional e Ciclo Financeiro"},
        ]
    },
    # === ALAVANCAGEM ===
    {
        "categoria": "Alavancagem",
        "metricas": [
            {"id": "alavancagem_financeira", "nome": "Alavancagem Financeira (GAF)", "coluna": "Alavancagem Financeira (GAF)"},
            {"id": "alavancagem_operacional", "nome": "Alavancagem Operacional (GAO)", "coluna": "Alavancagem Operacional (GAO)"},
            {"id": "alavancagem_total", "nome": "Alavancagem Total (GAT)", "coluna": "Alavancagem Total (GAT) - Cálculo Possível"},
        ]
    },
    # === OUTROS COMPONENTES ===
    {
        "categoria": "Outros Componentes",
        "metricas": [
            {"id": "contas_receber", "nome": "Contas a Receber (Circulante)", "coluna": "Contas a Receber (Circulante)"},
            {"id": "estoques", "nome": "Estoques", "coluna": "Estoques"},
            {"id": "fornecedores", "nome": "Fornecedores", "coluna": "Fornecedores"},
        ]
    },
]

class ChatIAPage(BasePage):
    """Página de chat com IA contextual a métricas específicas"""
    
    def __init__(self, df, financial_analyzer):
        super().__init__(df, financial_analyzer)
        self.ai_analyzer = AIAnalyzer()
        # Usar o DataFrame já processado do analyzer para garantir dados numéricos
        self.processed_df = self.analyzer.df
        # Inicializa registro de métricas disponíveis
        self.metrics_registry = self._build_metrics_registry()
    
    # --------------------------------------------------
    # Registro / Preparação de Métricas
    # --------------------------------------------------
    def _build_metrics_registry(self):
        registry = {}
        for categoria_info in _METRICAS_FINANCEIRAS:
            categoria = categoria_info["categoria"]
            for metrica in categoria_info["metricas"]:
                metrica_id = metrica["id"]
                coluna = metrica["coluna"]
                # Verificar se a coluna existe nos dados processados
                if coluna in self.processed_df.columns:
                    registry[metrica_id] = {
                        "nome": metrica["nome"],
                        "categoria": categoria,
                        "coluna": coluna,
                        "label": f"{categoria} • {metrica['nome']}"
                    }
        return registry
    
    def _get_metric_options(self):
        """Retorna lista de opções organizadas por categoria"""
        options = []
        for categoria_info in _METRICAS_FINANCEIRAS:
            categoria = categoria_info["categoria"]
            categoria_metrics = []
            for metrica in categoria_info["metricas"]:
                if metrica["id"] in self.metrics_registry:
                    categoria_metrics.append(self.metrics_registry[metrica["id"]]["label"])
            if categoria_metrics:
                options.extend(categoria_metrics)
        return options
    
    def _resolve_metric_id(self, label):
        """Resolve o ID da métrica pelo label selecionado"""
        for metric_id, meta in self.metrics_registry.items():
            if meta["label"] == label:
                return metric_id
        return None
    
    # --------------------------------------------------
    # Render Principal
    # --------------------------------------------------
    def render(self):
        st.title("🤖 Chat com IA - Análise de Métricas Financeiras")
        st.caption("Selecione uma métrica específica da base de dados e faça perguntas. A IA responderá com análises contextualizadas.")
        st.markdown("---")
        
        if not self.ai_analyzer.is_available():
            st.error("API Gemini não configurada.")
            return
        
        self._render_metric_selector()
        self._render_chat_interface()
        self.render_sidebar_info()
    
    # --------------------------------------------------
    # Seleção e Miniatura
    # --------------------------------------------------
    def _render_metric_selector(self):
        st.subheader("1️⃣ Seleção da Métrica")
        options = self._get_metric_options()
        if not options:
            st.warning("Nenhuma métrica disponível.")
            return
        selected_label = st.selectbox(
            "Selecione métrica para análise:",
            options,
            key="ai_metric_select"
        )
        metric_id = self._resolve_metric_id(selected_label)
        st.session_state.selected_metric_id = metric_id
        
        # Mostra informações da métrica
        if metric_id and metric_id in self.metrics_registry:
            meta = self.metrics_registry[metric_id]
            st.caption(f"**Categoria:** {meta['categoria']} | **Coluna:** {meta['coluna']}")
        
        st.markdown("---")
    # --------------------------------------------------
    # Preparação de Dados para IA (por métrica)
    # --------------------------------------------------
    def _prepare_metric_data(self, metric_id):
        """Prepara dados contextuais para uma métrica específica"""
        if metric_id not in self.metrics_registry:
            return {"erro": "métrica não encontrada"}
        
        meta = self.metrics_registry[metric_id]
        coluna = meta["coluna"]
        
        # Verifica se a coluna existe
        if coluna not in self.processed_df.columns:
            return {"erro": f"coluna '{coluna}' não encontrada nos dados"}
        
        # Prepara dados básicos da métrica
        try:
            df_metric = self.processed_df[['Ano', coluna]].copy()
            # Remove valores nulos
            df_metric = df_metric.dropna()
            
            if len(df_metric) == 0:
                return {"erro": f"não há dados válidos para a métrica '{meta['nome']}'"}
            
            # Garante que os valores sejam numéricos
            try:
                df_metric[coluna] = pd.to_numeric(df_metric[coluna], errors='coerce')
                df_metric = df_metric.dropna()  # Remove NaN após conversão
            except Exception as conv_error:
                return {"erro": f"erro na conversão dos dados para números: {str(conv_error)}"}
            
            if len(df_metric) == 0:
                return {"erro": f"todos os valores da métrica '{meta['nome']}' são inválidos"}
            
            # Dados principais
            data = {
                "métrica": meta["nome"],
                "categoria": meta["categoria"],  
                "coluna": coluna,
                "dados": df_metric.to_dict('records'),
                "estatísticas": {
                    "valor_atual": float(df_metric[coluna].iloc[-1]) if len(df_metric) > 0 else None,
                    "valor_anterior": float(df_metric[coluna].iloc[-2]) if len(df_metric) > 1 else None,
                    "média": float(df_metric[coluna].mean()),
                    "mínimo": float(df_metric[coluna].min()),
                    "máximo": float(df_metric[coluna].max()),
                    "tendência": "crescente" if len(df_metric) > 1 and df_metric[coluna].iloc[-1] > df_metric[coluna].iloc[-2] else "decrescente" if len(df_metric) > 1 else "estável",
                    "variacao_percentual": round(((df_metric[coluna].iloc[-1] / df_metric[coluna].iloc[-2]) - 1) * 100, 2) if len(df_metric) > 1 and df_metric[coluna].iloc[-2] != 0 else None
                }
            }
            
            # Adiciona contexto específico por categoria
            if "Patrimônio" in meta["categoria"] or "Estrutura" in meta["categoria"]:
                data["contexto"] = {
                    "tipo": "estrutura_patrimonial",
                    "benchmark_mercado": "Imobilizado representa ativos de longo prazo como máquinas, equipamentos, imóveis",
                    "interpretação": "Valores altos indicam empresa intensiva em capital; baixos indicam operação mais leve"
                }
            elif "Rentabilidade" in meta["categoria"]:
                data["contexto"] = {
                    "tipo": "rentabilidade",
                    "benchmark_mercado": "ROE > 15% excelente, 10-15% bom, < 10% preocupante",
                    "interpretação": "Valores maiores indicam melhor retorno aos acionistas"
                }
            elif "Liquidez" in meta["categoria"]:
                data["contexto"] = {
                    "tipo": "liquidez", 
                    "benchmark_mercado": "LC > 1.5 ótima, 1.0-1.5 adequada, < 1.0 risco de liquidez",
                    "interpretação": "Valores maiores indicam maior capacidade de honrar compromissos"
                }
            elif "Endividamento" in meta["categoria"]:
                data["contexto"] = {
                    "tipo": "endividamento",
                    "benchmark_mercado": "EG < 40% conservador, 40-60% moderado, > 60% alto risco",
                    "interpretação": "Valores menores indicam menor dependência de terceiros"
                }
            elif "Ciclos" in meta["categoria"] or "Prazo" in meta["categoria"]:
                data["contexto"] = {
                    "tipo": "ciclos_prazos",
                    "benchmark_mercado": "Prazos menores geralmente melhores para capital de giro",
                    "interpretação": "Analise conjunto: PMRE + PMRV - PMPC = Ciclo Financeiro"
                }
            elif "Alavancagem" in meta["categoria"]:
                data["contexto"] = {
                    "tipo": "alavancagem",
                    "benchmark_mercado": "GAF > 1 amplifica ganhos e perdas; quanto maior, maior o risco",
                    "interpretação": "Monitore em períodos de volatilidade de resultados"
                }
            else:
                data["contexto"] = {
                    "tipo": "outros",
                    "benchmark_mercado": "Compare com períodos anteriores e concorrentes do setor",
                    "interpretação": "Analise tendências e variações significativas"
                }
            
            return data
            
        except Exception as e:
            return {"erro": f"erro ao processar dados: {str(e)}"}
    
    # --------------------------------------------------
    # Chat
    # --------------------------------------------------
    def _init_chat_state(self):
        if 'ai_metric_chat_history' not in st.session_state:
            st.session_state.ai_metric_chat_history = []
    
    def _render_chat_interface(self):
        self._init_chat_state()
        st.subheader("2️⃣ Pergunte à IA sobre a Métrica")
        metric_id = st.session_state.get('selected_metric_id')
        if not metric_id:
            st.info("Selecione uma métrica primeiro.")
            return
        
        meta = self.metrics_registry.get(metric_id, {})
        placeholder_ex = f"Ex: Como evoluiu {meta.get('nome', 'esta métrica')}? Quais os principais insights? Como está em relação ao benchmark?"
        pergunta = st.text_area(
            "Sua pergunta:",
            placeholder=placeholder_ex,
            key="ai_metric_question",
            height=110
        )
        col_a, col_b, col_c = st.columns([1,1,1])
        with col_a:
            analisar = st.button("🚀 Analisar", type="primary")
        with col_b:
            if st.button("🧹 Limpar Histórico"):
                st.session_state.ai_metric_chat_history = []
                st.success("Histórico limpo")
                st.rerun()
        with col_c:
            st.download_button(
                "⬇️ Exportar Histórico",
                data=self._export_history_to_markdown(),
                file_name="chat_ia_metricas.md",
                mime="text/markdown",
                disabled=not st.session_state.ai_metric_chat_history
            )
        
        if analisar:
            if not pergunta.strip():
                st.warning("Digite uma pergunta.")
            else:
                with st.spinner("IA analisando..."):
                    metric_data = self._prepare_metric_data(metric_id)
                    resposta = self.ai_analyzer.generate_metric_insights(
                        metric_data=metric_data,
                        metric_id=metric_id,
                        df_filtrado=self.processed_df,
                        custom_question=pergunta
                    )
                    st.session_state.ai_metric_chat_history.append({
                        "metric_id": metric_id,
                        "metric_label": meta.get("nome", "Métrica"),
                        "pergunta": pergunta,
                        "resposta": resposta,
                        "ts": datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                    })
                    st.success("Análise concluída")
        
        self._render_history()
    
    def _render_history(self):
        if not st.session_state.ai_metric_chat_history:
            return
        st.markdown("---")
        st.subheader("💬 Histórico")
        for item in reversed(st.session_state.ai_metric_chat_history):
            with st.expander(f"{item['ts']} • {item['metric_label']}"):
                st.markdown(f"**Pergunta:** {item['pergunta']}")
                st.markdown("**Resposta da IA:**")
                st.markdown(item['resposta'])
    
    def _export_history_to_markdown(self):
        lines = ["# Histórico Chat IA (Métricas Financeiras)\n"]
        for item in st.session_state.ai_metric_chat_history:
            lines.append(f"## {item['ts']} - {item['metric_label']}")
            lines.append(f"**Pergunta:** {item['pergunta']}")
            lines.append("**Resposta:**")
            lines.append(item['resposta'])
            lines.append("\n---\n")
        return "\n".join(lines)
