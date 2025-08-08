"""
Página de Análise de Liquidez
"""

import streamlit as st
from pages.base_page import BasePage

class AnaliseLiquidezPage(BasePage):
    """Página especializada em análise de liquidez"""

    def render(self):
        st.title("🛡️ Análise de Liquidez")
        st.markdown("---")
        self._render_description()
        self._render_radar_chart()
        self._render_table()
        self.render_sidebar_info()

    def _render_description(self):
        st.markdown(
            """
            ### 💧 **Indicadores de Liquidez**
            Avaliam a capacidade de a empresa honrar seus compromissos de curto e longo prazo.
            - **Liquidez Geral (LG)**: Capacidade total de pagamento (curto + longo prazo)
            - **Liquidez Corrente (LC)**: Capacidade de pagar obrigações de curto prazo
            - **Liquidez Seca (LS)**: LC desconsiderando estoques (mais conservadora)
            - **Liquidez Imediata (LI)**: Disponibilidades frente às dívidas de curto prazo
            """
        )

    def _render_radar_chart(self):
        try:
            fig = self.analyzer.create_liquidez_radar()
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            self.show_error(f"Erro ao carregar radar: {e}")

    def _render_table(self):
        try:
            cols = [
                'Ano', 'Liquidez Geral (LG)', 'Liquidez Corrente (LC) ',
                'Liquidez Seca (LS)', 'Liquidez Imediata (LI)'
            ]
            disponiveis = [c for c in cols if c in self.df.columns]
            if len(disponiveis) < 2:
                self.show_warning("Colunas de liquidez insuficientes para tabela")
                return
            st.subheader("📊 Tabela de Indicadores")
            st.dataframe(self.df[disponiveis].set_index('Ano'), use_container_width=True)
        except Exception as e:
            self.show_error(f"Erro na tabela: {e}")
