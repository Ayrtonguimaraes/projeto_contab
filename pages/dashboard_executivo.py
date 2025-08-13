"""
Página do Dashboard Executivo - Versão Simplificada
"""

import streamlit as st
import pandas as pd
from pages.base_page import BasePage

class DashboardExecutivoPage(BasePage):
    """Página principal do dashboard executivo simplificado - apenas cards"""
    
    def render(self):
        """Renderiza a página do dashboard executivo simplificado (apenas cards)."""
        st.title("📊 Cards das métricas")
        
        # Verificar se temos dados suficientes (2023 e 2024)
        df = self.analyzer.df.sort_values('Ano')
        if len(df) < 2:
            st.warning("⚠️ Necessário pelo menos 2 anos de dados para comparação (2023 e 2024)")
            self.render_sidebar_info()
            return
            
        # KPIs principais em cards
        self._render_all_metrics_cards()
        
        # Sidebar info
        self.render_sidebar_info()
    
    # -------------------- CARDS DE MÉTRICAS --------------------
    def _render_all_metrics_cards(self):
        """Renderiza todos os cards de métricas com comparação 2024 vs 2023"""
        st.markdown("### 📊 **Todas as Métricas Financeiras - Comparação 2024 vs 2023**")
        st.markdown("*Visualização completa de 37 indicadores organizados por categoria*")
        
        # CSS para estilizar os cards
        st.markdown("""
        <style>
        .metric-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #e0e6ed;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
            margin-bottom: 10px;
        }
        .metric-value {
            font-size: 1.8rem;
            font-weight: bold;
            color: #2c3e50;
            margin: 5px 0;
        }
        .metric-label {
            font-size: 0.9rem;
            color: #34495e;
            margin-bottom: 8px;
        }
        .metric-delta-positive {
            font-size: 1.1rem;
            color: #27ae60;
            font-weight: bold;
        }
        .metric-delta-negative {
            font-size: 1.1rem;
            color: #e74c3c;
            font-weight: bold;
        }
        .metric-delta-neutral {
            font-size: 1.1rem;
            color: #7f8c8d;
            font-weight: bold;
        }
        </style>
        """, unsafe_allow_html=True)
        
        df = self.analyzer.df.sort_values('Ano')
        if len(df) < 2:
            st.error("Dados insuficientes para comparação")
            return
            
        prev, cur = df.iloc[-2], df.iloc[-1]
        ano_prev, ano_cur = int(prev['Ano']), int(cur['Ano'])
        
        # Definir TODAS as métricas disponíveis organizadas por categoria
        metricas = {
            # === ESTRUTURA PATRIMONIAL ===
            "💰 Ativo Total": 'Ativo Total',
            "�️ Imobilizado": 'Imobilizado',
            "📊 Passivo Circulante": 'Passivo Circulante',
            "📈 Passivo Não Circulante": 'Passivo Não Circulante',
            "🏦 Patrimônio Líquido": 'Patrimônio Líquido',
            "💰 Caixa e Equivalentes": 'Caixa e Equivalentes de Caixa',
            "📦 Estoques": 'Estoques',
            "💳 Contas a Receber": 'Contas a Receber (Circulante)',
            "🔮 Realizável Longo Prazo": 'Realizável a Longo Prazo',
            
            # === RESULTADO E PERFORMANCE ===
            "💵 Receita Líquida": 'Receita Líquida',
            "💎 Lucro Líquido": 'Lucro Líquido',
            "🔥 Lucro Operacional": 'Lucro Operacional',
            "⚡ Lucro Antes Impostos": 'Lucro Antes dos Impostos',
            "💸 CPV": 'Custo dos Produtos Vendidos (CPV)',
            "🏪 Fornecedores": 'Fornecedores',
            
            # === LIQUIDEZ ===
            "🛡️ Liquidez Corrente": 'Liquidez Corrente (LC) ',
            "💧 Liquidez Imediata": 'Liquidez Imediata (LI)',
            "⚖️ Liquidez Geral": 'Liquidez Geral (LG)',
            "🔒 Liquidez Seca": 'Liquidez Seca (LS)',
            
            # === RENTABILIDADE ===
            "📈 ROE": 'Rentabilidade do Patrimônio Líquido (ROE) ',
            "🎯 ROA": 'Rentabilidade do Ativo (ROA ou ROI)',
            "💫 Margem Líquida": 'Margem Líquida (ML)',
            "🔄 Giro do Ativo": 'Giro do Ativo (GA)',
            "🔢 Multiplicador MAF": 'Multiplicador de Alavancagem Financeira (MAF)',
            "📊 ROI DuPont": 'Análise do ROI (Método DuPont) ',
            
            # === ENDIVIDAMENTO ===
            "⚠️ Endividamento Geral": 'Endividamento Geral (EG)',
            "🔗 Participação Capital Terceiros": 'Participação de Capitais de Terceiros (PCT) – Grau de Endividamento',
            "⚖️ Composição Endividamento": 'Composição do Endividamento (CE)',
            "🏗️ Imobilização PL": 'Grau de Imobilização do Patrimônio Líquido (ImPL)',
            "🔧 Imobilização Recursos NC": 'Grau de Imobilização dos Recursos não Correntes (IRNC) ',
            
            # === CICLOS OPERACIONAIS ===
            "📦 PMRE (dias)": 'Prazo Médio de Renovação dos Estoques (PMRE) ',
            "💳 PMRV (dias)": 'Prazo Médio de Recebimento das Vendas (PMRV) ',
            "💸 PMPC (dias)": 'Prazo Médio de Pagamento das Compras (PMPC) ',
            "⏰ Ciclo Financeiro": 'Ciclo Operacional e Ciclo Financeiro',
            
            # === ALAVANCAGEM ===
            "💪 Alavancagem Financeira": 'Alavancagem Financeira (GAF)',
            "⚙️ Alavancagem Operacional": 'Alavancagem Operacional (GAO)',
            "🚀 Alavancagem Total": 'Alavancagem Total (GAT) - Cálculo Possível'
        }
        
        # Renderizar cards em colunas
        cols_per_row = 4
        metrics_list = [(label, col) for label, col in metricas.items() if col in df.columns]
        
        for i in range(0, len(metrics_list), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, (label, col_name) in enumerate(metrics_list[i:i+cols_per_row]):
                with cols[j]:
                    self._render_metric_card(label, col_name, prev, cur, ano_prev, ano_cur)
    
    def _render_metric_card(self, label, col_name, prev, cur, ano_prev, ano_cur):
        """Renderiza um card individual de métrica com estilo customizado"""
        try:
            val_prev = prev[col_name]
            val_cur = cur[col_name]
            
            # Verificar se os valores são válidos
            if pd.isna(val_cur) or pd.isna(val_prev):
                self._render_na_card(label)
                return
            
            # Calcular variação percentual
            if val_prev != 0 and val_prev is not None:
                variacao_pct = ((val_cur - val_prev) / abs(val_prev)) * 100
            else:
                variacao_pct = 0
            
            # Formatação inteligente baseada no tipo de métrica e grandeza correta
            
            # DADOS BRUTOS (1-15): R$ Milhões
            if any(x in col_name.lower() for x in ['ativo', 'patrimônio', 'passivo', 'receita', 'lucro', 'caixa', 'estoque', 'imobilizado', 'cpv', 'fornecedor', 'contas a receber', 'realizável']):
                # Valores monetários em milhões
                if val_cur >= 1000:
                    valor_formatado = f"R$ {val_cur/1000:.1f}B"  # Bilhões
                else:
                    valor_formatado = f"R$ {val_cur:.0f}M"  # Milhões
            
            # ESTRUTURA DE CAPITAL (16,18,19,20): Porcentagem (%) - exceto PCT(17)
            elif any(x in col_name.lower() for x in ['endividamento geral', 'composição', 'imobilização']):
                valor_formatado = f"{val_cur:.1%}"
            
            # LIQUIDEZ (21-24): Números (Ex: 0,35)
            elif any(x in col_name.lower() for x in ['liquidez']):
                valor_formatado = f"{val_cur:.2f}"
            
            # RENTABILIDADE - Porcentagens (26,27,28,30): %
            elif any(x in col_name.lower() for x in ['margem líquida', 'roa', 'roe', 'dupont']):
                valor_formatado = f"{val_cur:.1%}"
            
            # RENTABILIDADE - Números (25,29): Giro do Ativo, MAF
            elif any(x in col_name.lower() for x in ['giro do ativo', 'multiplicador']):
                valor_formatado = f"{val_cur:.2f}"
            
            # ALAVANCAGEM (35-37): Números (Ex: 0,39, 6,36, 2,47)
            elif any(x in col_name.lower() for x in ['alavancagem']):
                valor_formatado = f"{val_cur:.2f}"
            
            # PARTICIPAÇÃO DE CAPITAIS DE TERCEIROS (17): Número (Ex: 2,06)
            elif 'participação de capitais de terceiros' in col_name.lower():
                valor_formatado = f"{val_cur:.2f}"
            
            # PRAZOS MÉDIOS E CICLOS (31-34): Dias
            elif any(x in col_name.lower() for x in ['pmre', 'pmrv', 'pmpc', 'ciclo']):
                valor_formatado = f"{val_cur:.0f} dias"
            
            else:
                # Formato padrão para outros valores
                valor_formatado = f"{val_cur:.2f}"
            
            # Definir classe CSS da variação (considerando lógica de negócios)
            is_positive_metric = self._is_positive_metric(col_name, variacao_pct)
            
            if is_positive_metric:
                delta_class = "metric-delta-positive"
                delta_symbol = "↗"
            elif variacao_pct == 0:
                delta_class = "metric-delta-neutral" 
                delta_symbol = "→"
            else:
                delta_class = "metric-delta-negative"
                delta_symbol = "↘"
            
            # Renderizar card personalizado
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{valor_formatado}</div>
                <div class="{delta_class}">{delta_symbol} {variacao_pct:+.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
            
        except (KeyError, TypeError, ValueError, AttributeError) as e:
            self._render_na_card(label, str(e))
    
    def _is_positive_metric(self, col_name, variacao_pct):
        """Determina se uma variação é positiva baseada na natureza da métrica"""
        if variacao_pct == 0:
            return False
            
        # Métricas onde AUMENTO é POSITIVO
        positive_increase = [
            'ativo total', 'patrimônio líquido', 'receita', 'lucro', 'caixa',
            'roe', 'roa', 'margem líquida', 'giro', 'liquidez', 'maf'
        ]
        
        # Métricas onde AUMENTO é NEGATIVO  
        negative_increase = [
            'endividamento', 'pct', 'pmre', 'pmrv', 'ciclo', 'cpv',
            'passivo', 'impl'  # Alto endividamento e imobilização são ruins
        ]
        
        col_lower = col_name.lower()
        
        # Verificar se é métrica de resultado positivo
        for term in positive_increase:
            if term in col_lower:
                return variacao_pct > 0
        
        # Verificar se é métrica de resultado negativo
        for term in negative_increase:
            if term in col_lower:
                return variacao_pct < 0
        
        # Padrão: aumento é positivo
        return variacao_pct > 0
    
    def _render_na_card(self, label, error_msg="Dados indisponíveis"):
        """Renderiza card para valores não disponíveis"""
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">N/A</div>
            <div class="metric-delta-neutral">— {error_msg}</div>
        </div>
        """, unsafe_allow_html=True)