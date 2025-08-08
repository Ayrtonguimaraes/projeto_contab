"""
Classe base para todas as páginas do dashboard
"""

import streamlit as st
from abc import ABC, abstractmethod

class BasePage(ABC):
    """Classe base abstrata para páginas do dashboard"""
    
    def __init__(self, df, financial_analyzer):
        """
        Inicializa a página
        
        Args:
            df: DataFrame com os dados
            financial_analyzer: Instância do FinancialAnalyzer
        """
        self.df = df
        self.analyzer = financial_analyzer
    
    @abstractmethod
    def render(self):
        """Método abstrato que deve ser implementado por cada página"""
        pass
    
    def render_sidebar_info(self):
        """Renderiza informações na sidebar (comum a todas as páginas)"""
        with st.sidebar:
            st.markdown("### 📊 **Informações dos Dados**")
            
            if self.df is not None and not self.df.empty:
                if hasattr(self.df, 'Ano'):  # Dados financeiros
                    anos = self.df['Ano'].unique()
                    st.success(f"✅ **Dados financeiros:** {len(anos)} anos")
                    st.info(f"📅 **Anos:** {', '.join(map(str, sorted(anos)))}")
                else:  # Dados contábeis
                    total_records = len(self.df)
                    date_range = f"{self.df['Data'].min().strftime('%m/%Y')} - {self.df['Data'].max().strftime('%m/%Y')}"
                    st.success(f"✅ **{total_records:,}** registros carregados")
                    st.info(f"📅 Período: **{date_range}**")
            else:
                st.error("❌ Nenhum dado carregado")
    
    def show_loading(self, message="Carregando..."):
        """Exibe indicador de carregamento"""
        return st.spinner(message)
    
    def show_error(self, message):
        """Exibe mensagem de erro"""
        st.error(f"❌ {message}")
    
    def show_success(self, message):
        """Exibe mensagem de sucesso"""
        st.success(f"✅ {message}")
    
    def show_info(self, message):
        """Exibe mensagem informativa"""
        st.info(f"ℹ️ {message}")
    
    def show_warning(self, message):
        """Exibe mensagem de aviso"""
        st.warning(f"⚠️ {message}")
