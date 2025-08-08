"""
Página de Indicadores Gerais Consolidada
"""

import streamlit as st
from pages.base_page import BasePage
import pandas as pd

class IndicadoresGeraisPage(BasePage):
    """Mostra tabela consolidada de todos os indicadores com variações."""

    def render(self):
        st.title("📋 Indicadores Gerais")
        st.caption("Visão tabular consolidada de todos os indicadores financeiros e operacionais com variação ano a ano.")
        st.markdown("---")

        tabela = self.analyzer.get_indicadores_tabela()
        if tabela.empty:
            st.info("Necessário pelo menos 2 anos para calcular variações.")
            return

        # Formatação
        df_display = tabela.copy()
        # Definir quais indicadores são percentuais (heurística por presença de 'Liquidez', 'Rentabilidade', 'Margem', 'Giro', 'Alavancagem', 'Grau', 'ROA', 'ROE', '%', 'MAF')
        percent_keywords = [
            'Liquidez', 'Rentabilidade', 'Margem', 'Giro', 'Alavancagem', 'Grau', 'ROA', 'ROE', 'MAF', 'PCT'
        ]

        def _is_percent(ind):
            return any(k in ind for k in percent_keywords)

        def fmt_val(indicador, v):
            if v is None:
                return '—'
            try:
                if _is_percent(indicador):
                    return f"{v:.2%}" if v <= 1.5 else f"{v:.2f}"  # heurística (valores já percentuais vs índice >1)
                return f"{v:,.0f}".replace(',', '.')
            except Exception:
                return v

        # Aplicar formatação
        df_display['Ano Anterior'] = df_display.apply(lambda r: fmt_val(r['Indicador'], r['Ano Anterior']), axis=1)
        df_display['Ano Atual'] = df_display.apply(lambda r: fmt_val(r['Indicador'], r['Ano Atual']), axis=1)
        df_display['Variação Abs'] = df_display.apply(lambda r: fmt_val(r['Indicador'], r['Variação Abs']), axis=1)
        df_display['Variação %'] = df_display['Variação %'].apply(lambda v: '—' if v is None else f"{v:.1f}%")

        st.subheader("🧮 Tabela Consolidada")
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        # Destaques automáticos
        st.markdown("### 🔎 Destaques Automáticos")
        top_var = tabela.sort_values('Variação %', ascending=False).head(3)
        worst_var = tabela.sort_values('Variação %', ascending=True).head(3)
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Maiores Altas (%):**")
            for _, row in top_var.iterrows():
                if row['Variação %'] is not None:
                    st.markdown(f"✅ {row['Indicador']}: **{row['Variação %']:.1f}%**")
        with col2:
            st.write("**Maiores Quedas (%):**")
            for _, row in worst_var.iterrows():
                if row['Variação %'] is not None:
                    st.markdown(f"🔻 {row['Indicador']}: **{row['Variação %']:.1f}%**")

        # Integração opcional com IA
        with st.expander("🤖 Analisar Tabela com IA"):
            st.write("Gera contexto estruturado para perguntas no Chat com IA.")
            if st.button("📨 Enviar para Chat IA"):
                # Armazena tabela serializada no session_state
                st.session_state.ai_indicadores_context = tabela.to_dict('records')
                st.success("Contexto armazenado. Abra 'Chat com IA' e pergunte usando este conjunto.")

        self.render_sidebar_info()
