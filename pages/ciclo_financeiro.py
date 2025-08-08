"""
Página de Ciclo Financeiro
"""

import streamlit as st
from pages.base_page import BasePage

class CicloFinanceiroPage(BasePage):
    """Página para análise do ciclo operacional e financeiro"""

    def render(self):
        st.title("⏱️ Ciclo Financeiro")
        st.markdown("---")
        self._render_description()
        self._render_charts()
        self.render_sidebar_info()

    def _render_description(self):
        st.markdown(
            """
            ### 🔄 **Componentes do Ciclo**
            - **PMRE**: Prazo Médio de Renovação de Estoques
            - **PMRV**: Prazo Médio de Recebimento de Vendas
            - **PMPC**: Prazo Médio de Pagamento de Compras
            - **Ciclo Operacional** = PMRE + PMRV
            - **Ciclo Financeiro** = Ciclo Operacional - PMPC
            """
        )

    def _render_charts(self):
        try:
            fig = self.analyzer.create_ciclo_financeiro()
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            self.show_error(f"Erro ao carregar gráficos: {e}")
