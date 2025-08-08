"""
Página do Dashboard Executivo
"""

import streamlit as st
from pages.base_page import BasePage

class DashboardExecutivoPage(BasePage):
    """Página principal do dashboard executivo"""
    
    def render(self):
        """Renderiza a página do dashboard executivo"""
        st.title("🏠 Dashboard Executivo")
        st.markdown("### Visão geral dos principais indicadores financeiros")
        st.markdown("---")
        
        # Renderizar KPIs principais
        self._render_kpis()
        
        st.markdown("---")
        
        # Renderizar gráficos principais
        self._render_main_charts()
        
        # Renderizar informações na sidebar
        self.render_sidebar_info()
    
    def _render_kpis(self):
        """Renderiza os KPIs principais"""
        st.subheader("📈 KPIs Principais")
        
        try:
            kpis = self.analyzer.get_kpis_principais()
            
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
                    "💎 Lucro Líquido", 
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
                
        except Exception as e:
            self.show_error(f"Erro ao carregar KPIs: {str(e)}")
    
    def _render_main_charts(self):
        """Renderiza os gráficos principais"""
        try:
            # Gráfico de evolução patrimonial
            st.subheader("💰 Evolução Patrimonial")
            fig_evolucao = self.analyzer.create_evolucao_patrimonial()
            st.plotly_chart(fig_evolucao, use_container_width=True)
            
            # Análise de rentabilidade resumida
            st.subheader("📈 Visão Geral da Rentabilidade")
            fig_rent = self.analyzer.create_rentabilidade_chart()
            st.plotly_chart(fig_rent, use_container_width=True)
            
        except Exception as e:
            self.show_error(f"Erro ao carregar gráficos: {str(e)}")
