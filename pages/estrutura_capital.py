"""
Página de Estrutura de Capital
"""

import streamlit as st
from pages.base_page import BasePage

class EstruturaCapitalPage(BasePage):
    """Página para análise da estrutura de capital e endividamento"""

    def render(self):
        st.title("🏦 Estrutura de Capital")
        st.markdown("---")
        self._render_description()
        self._render_main_chart()
        self.render_sidebar_info()

    def _render_description(self):
        st.markdown(
            """
            ### 🏗️ **Indicadores de Estrutura de Capital**
            Avaliam o nível de alavancagem e a composição do financiamento da empresa.
            - **Endividamento Geral (EG)**: Proporção de dívida sobre o total de ativos
            - **Composição do Endividamento (CE)**: Peso do passivo circulante no total das dívidas
            - **Participação de Capitais de Terceiros (PCT)**: Dependência de capital de terceiros
            """
        )

    def _render_main_chart(self):
        try:
            fig = self.analyzer.create_estrutura_capital()
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            self.show_error(f"Erro ao carregar gráfico: {e}")
