"""
Página de Visão Geral (Heatmap)
"""

import streamlit as st
from pages.base_page import BasePage

class VisaoGeralPage(BasePage):
    """Página de visão consolidada dos indicadores (heatmap)"""

    def render(self):
        st.title("🌡️ Visão Geral - Heatmap")
        st.markdown("---")
        self._render_description()
        self._render_heatmap()
        self.render_sidebar_info()

    def _render_description(self):
        st.markdown(
            """
            ### 🌐 **Mapa de Calor de Indicadores**
            Visualização comparativa dos principais indicadores ao longo dos anos.
            Cores mais intensas indicam valores relativamente mais altos dentro de cada linha.
            """
        )

    def _render_heatmap(self):
        try:
            fig = self.analyzer.create_heatmap_indicadores()
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            self.show_error(f"Erro ao carregar heatmap: {e}")
