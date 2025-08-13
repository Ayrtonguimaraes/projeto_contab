"""
Página do Dashboard Executivo - Versão Simplificada
"""

import streamlit as st
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
        st.markdown("### 📊 **Indicadores Financeiros - Comparação 2024 vs 2023**")
        
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
        
        # Definir todas as métricas disponíveis
        metricas = {
            # Estrutura Patrimonial
            "💰 Ativo Total": 'Ativo Total',
            "🏦 Patrimônio Líquido": 'Patrimônio Líquido', 
            "📊 Passivo Circulante": 'Passivo Circulante',
            "📈 Passivo Não Circulante": 'Passivo Não Circulante',
            
            # Resultado
            "💵 Receita Líquida": 'Receita Líquida',
            "💎 Lucro Líquido": 'Lucro Líquido',
            "🔥 Lucro Operacional": 'Lucro Operacional',
            "⚡ Lucro Antes dos Impostos": 'Lucro Antes dos Impostos',
            
            # Liquidez
            "🛡️ Liquidez Corrente": 'Liquidez Corrente (LC) ',
            "💧 Liquidez Imediata": 'Liquidez Imediata (LI)',
            "⚖️ Liquidez Geral": 'Liquidez Geral (LG)',
            
            # Rentabilidade
            "📈 ROE": 'Rentabilidade do Patrimônio Líquido (ROE) ',
            "🎯 ROA": 'Rentabilidade do Ativo (ROA)',
            "💫 Margem Líquida": 'Margem Líquida (ML)',
            "🔄 Giro do Ativo": 'Giro do Ativo (GA)',
            "🔢 Multiplicador MAF": 'Multiplicador de Alavancagem Financeira (MAF)',
            
            # Endividamento
            "⚠️ Endividamento Geral": 'Endividamento Geral (EG)',
            
            # Ciclos
            "📦 PMRE (dias)": 'Prazo Médio de Renovação dos Estoques (PMRE) ',
            "💳 PMRV (dias)": 'Prazo Médio de Recebimento das Vendas (PMRV) ',
            "💸 PMPC (dias)": 'Prazo Médio de Pagamento das Compras (PMPC) ',
            "⏰ Ciclo Financeiro": 'Ciclo Operacional e Ciclo Financeiro'
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
            
            # Calcular variação percentual
            if val_prev != 0 and val_prev is not None:
                variacao_pct = ((val_cur - val_prev) / abs(val_prev)) * 100
            else:
                variacao_pct = 0
            
            # Formatação do valor atual
            if 'R$' in label or any(x in col_name for x in ['Ativo', 'Patrimônio', 'Passivo', 'Receita', 'Lucro', 'Caixa']):
                valor_formatado = f"R$ {val_cur:,.0f}".replace(',', '.')
            elif any(x in col_name for x in ['ML', 'ROE', 'ROA', 'EG']) or '%' in label:
                valor_formatado = f"{val_cur:.1%}"
            elif 'dias' in label:
                valor_formatado = f"{val_cur:.0f} dias"
            else:
                valor_formatado = f"{val_cur:.2f}"
            
            # Definir classe CSS da variação
            if variacao_pct > 0:
                delta_class = "metric-delta-positive"
                delta_symbol = "↗"
            elif variacao_pct < 0:
                delta_class = "metric-delta-negative"
                delta_symbol = "↘"
            else:
                delta_class = "metric-delta-neutral"
                delta_symbol = "→"
            
            # Renderizar card personalizado
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{valor_formatado}</div>
                <div class="{delta_class}">{delta_symbol} {variacao_pct:+.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
            
        except (KeyError, TypeError, ValueError):
            # Card de erro
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">N/A</div>
                <div class="metric-delta-neutral">— Dados indisponíveis</div>
            </div>
            """, unsafe_allow_html=True)