"""
Gerenciador central de páginas
"""

from pages.dashboard_executivo import DashboardExecutivoPage
from pages.analise_rentabilidade import AnaliseRentabilidadePage
from pages.chat_ia import ChatIAPage
from pages.analise_liquidez import AnaliseLiquidezPage
from pages.estrutura_capital import EstruturaCapitalPage
from pages.ciclo_financeiro import CicloFinanceiroPage
from pages.analise_dupont import AnaliseDupontPage
from pages.indicadores_gerais import IndicadoresGeraisPage

class PageManager:
    """Gerenciador central para todas as páginas"""
    
    def __init__(self):
        self.pages = {}
        self._register_pages()
    
    def _register_pages(self):
        """Registra todas as páginas disponíveis"""
        self.pages = {
            "dashboard": DashboardExecutivoPage,
            "ai_chat": ChatIAPage,
            "rentabilidade": AnaliseRentabilidadePage,
            "liquidez": AnaliseLiquidezPage,
            "capital": EstruturaCapitalPage,
            "ciclo": CicloFinanceiroPage,
            "dupont": AnaliseDupontPage,
            "indicadores": IndicadoresGeraisPage,
        }
    
    def get_page_class(self, page_key):
        page_class = self.pages.get(page_key)
        # Auto tentativa de (re)registro se a chave 'indicadores' não estiver presente devido a cache de módulo
        if not page_class and page_key == 'indicadores':
            try:
                from importlib import reload
                import pages.indicadores_gerais as indicadores_mod
                reload(indicadores_mod)
                self.pages['indicadores'] = indicadores_mod.IndicadoresGeraisPage
                page_class = self.pages.get(page_key)
            except Exception:
                pass
        return page_class
    
    def render_page(self, page_key, df, financial_analyzer):
        page_class = self.get_page_class(page_key)
        if page_class:
            page_instance = page_class(df, financial_analyzer)
            page_instance.render()
        else:
            import streamlit as st
            st.error(f"Página '{page_key}' não encontrada")
            st.caption(f"Debug: páginas registradas = {list(self.pages.keys())}")
    
    def get_available_pages(self):
        return list(self.pages.keys())
