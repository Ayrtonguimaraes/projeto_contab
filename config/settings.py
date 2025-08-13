"""
Configurações centralizadas da aplicação
"""

import streamlit as st

class AppConfig:
    """Configurações principais da aplicação"""
    
    PAGE_CONFIG = {
        "page_title": "Dashboard de Análise Financeira Corporativa",
        "page_icon": "📊",
        "layout": "wide",
        "initial_sidebar_state": "expanded"
    }
    
    DATA_CONFIG = {
        "csv_file": "contab_ia.csv",
        "separator": ";",
        "decimal": ","
    }
    
    # Navegação reorganizada para evidenciar o Chat com IA como funcionalidade central
    NAVIGATION = {
        "📊 Cards das métricas": "dashboard",
        "🤖 Chat com IA": "ai_chat",
        "📋 Indicadores": "indicadores"
    }
    
    @staticmethod
    def configure_page():
        """Configura a página Streamlit"""
        st.set_page_config(**AppConfig.PAGE_CONFIG)
    
    @staticmethod
    def get_page_keys():
        """Retorna as chaves das páginas disponíveis"""
        return list(AppConfig.NAVIGATION.keys())
    
    @staticmethod
    def get_page_value(page_name):
        """Retorna o valor da página pelo nome"""
        return AppConfig.NAVIGATION.get(page_name)
