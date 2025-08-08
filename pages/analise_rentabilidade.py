"""
Página de Análise de Rentabilidade
"""

import streamlit as st
from pages.base_page import BasePage

class AnaliseRentabilidadePage(BasePage):
    """Página especializada em análise de rentabilidade"""
    
    def render(self):
        """Renderiza a página de análise de rentabilidade"""
        st.title("📈 Análise de Rentabilidade")
        st.markdown("---")
        
        # Descrição dos indicadores
        self._render_description()
        
        # Gráfico principal
        self._render_main_chart()
        
        # Análise comparativa
        self._render_comparative_analysis()
        
        # Renderizar informações na sidebar
        self.render_sidebar_info()
    
    def _render_description(self):
        """Renderiza a descrição dos indicadores"""
        st.markdown("""
        ### 🎯 **Indicadores de Rentabilidade**
        
        - **ROE (Return on Equity)**: Retorno sobre o Patrimônio Líquido
        - **ROA (Return on Assets)**: Retorno sobre os Ativos
        - **Margem Líquida**: Percentual do lucro em relação à receita
        """)
    
    def _render_main_chart(self):
        """Renderiza o gráfico principal de rentabilidade"""
        try:
            fig = self.analyzer.create_rentabilidade_chart()
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            self.show_error(f"Erro ao carregar gráfico de rentabilidade: {str(e)}")
    
    def _render_comparative_analysis(self):
        """Renderiza análise comparativa entre anos"""
        try:
            if 'Ano' not in self.df.columns:
                self.show_warning("Análise comparativa disponível apenas para dados financeiros")
                return
            
            anos = self.df['Ano'].tolist()
            if len(anos) < 2:
                self.show_info("Análise comparativa requer dados de pelo menos 2 anos")
                return
            
            ano_atual = max(anos)
            ano_anterior = min(anos)
            
            dados_atual = self.df[self.df['Ano'] == ano_atual].iloc[0]
            dados_anterior = self.df[self.df['Ano'] == ano_anterior].iloc[0]
            
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
                
                # Formatação com cores para variações
                roe_color = "🟢" if roe_var >= 0 else "🔴"
                roa_color = "🟢" if roa_var >= 0 else "🔴"
                ml_color = "🟢" if ml_var >= 0 else "🔴"
                
                st.write(f"**ROE:** {roe_color} {roe_var:+.1%}")
                st.write(f"**ROA:** {roa_color} {roa_var:+.1%}")
                st.write(f"**Margem Líquida:** {ml_color} {ml_var:+.1%}")
                
        except Exception as e:
            self.show_error(f"Erro na análise comparativa: {str(e)}")
