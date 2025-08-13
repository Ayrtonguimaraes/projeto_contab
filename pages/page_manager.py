"""
Gerenciador central de páginas
"""

from pages.dashboard_executivo import DashboardExecutivoPage
from pages.chat_ia import ChatIAPage
from pages.indicadores import IndicadoresPage

class PageManager:
    """Gerenciador central para todas as páginas"""
    
    def __init__(self):
        self.pages = {}
        self._register_pages()
    
    def _register_pages(self):
        """Registra páginas disponíveis (pós-unificação)"""
        self.pages = {
            "dashboard": DashboardExecutivoPage,
            "ai_chat": ChatIAPage,
            "indicadores": IndicadoresPage,
        }
        try:
            print("[PageManager] Páginas registradas:", list(self.pages.keys()))
        except Exception:
            pass
    
    def get_page_class(self, page_key):
        try:
            print(f"[PageManager] get_page_class chamado para: {page_key}")
        except Exception:
            pass
        return self.pages.get(page_key)
    
    def render_page(self, page_key, df, financial_analyzer):
        page_class = self.get_page_class(page_key)
        if page_class:
            try:
                print(f"[PageManager] Renderizando página: {page_key} -> {page_class.__name__}")
            except Exception:
                pass
            page_instance = page_class(df, financial_analyzer)
            page_instance.render()
        else:
            import streamlit as st
            st.error(f"Página '{page_key}' não encontrada")
            st.caption(f"Debug keys atuais: {list(self.pages.keys())}")
    
    def get_available_pages(self):
        return list(self.pages.keys())
