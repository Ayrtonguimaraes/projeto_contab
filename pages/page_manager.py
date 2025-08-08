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
from pages.visao_geral import VisaoGeralPage

class PageManager:
    """Gerenciador central para todas as páginas"""
    
    def __init__(self):
        self.pages = {}
        self._register_pages()
    
    def _register_pages(self):
        """Registra todas as páginas disponíveis"""
        self.pages = {
            "dashboard": DashboardExecutivoPage,
            "rentabilidade": AnaliseRentabilidadePage,
            "liquidez": AnaliseLiquidezPage,
            "capital": EstruturaCapitalPage,
            "ciclo": CicloFinanceiroPage,
            "dupont": AnaliseDupontPage,
            "heatmap": VisaoGeralPage,
            "ai_chat": ChatIAPage,
        }
    
    def get_page_class(self, page_key):
        return self.pages.get(page_key)
    
    def render_page(self, page_key, df, financial_analyzer):
        page_class = self.get_page_class(page_key)
        if page_class:
            page_instance = page_class(df, financial_analyzer)
            page_instance.render()
        else:
            import streamlit as st
            st.error(f"Página '{page_key}' não encontrada")
    
    def get_available_pages(self):
        return list(self.pages.keys())
