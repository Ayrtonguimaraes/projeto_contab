"""
Página de Análise DuPont
"""

import streamlit as st
from pages.base_page import BasePage

class AnaliseDupontPage(BasePage):
    """Página para análise detalhada do modelo DuPont"""

    def render(self):
        st.title("🔍 Análise DuPont")
        st.markdown("---")
        self._render_description()
        self._render_main_chart()
        self.render_sidebar_info()

    def _render_description(self):
        st.markdown(
            """
            ### 🧩 **Modelo DuPont**
            Decompõe o ROE em seus principais direcionadores:
            - **Margem Líquida**: Eficiência operacional
            - **Giro do Ativo**: Eficiência no uso dos ativos
            - **Multiplicador de Alavancagem (MAF)**: Efeito da estrutura de capital
            """
        )

    def _render_main_chart(self):
        try:
            fig = self.analyzer.create_analise_dupont()
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            self.show_error(f"Erro ao carregar gráfico: {e}")
