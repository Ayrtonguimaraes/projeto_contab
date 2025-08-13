"""
Página de Indicadores com Pré-visualização de Excel
"""

import streamlit as st
import pandas as pd
from pages.base_page import BasePage
import io

class IndicadoresPage(BasePage):
    """Página de indicadores com funcionalidade de preview de planilhas Excel"""
    
    def render(self):
        """Renderiza a página de indicadores com upload e preview de Excel"""
        st.title("📋 Indicadores")
        
        # Seção principal de upload e preview
        self._render_excel_preview_section()
        
        # Sidebar com informações
        self.render_sidebar_info()
    
    def _render_excel_preview_section(self):
        """Renderiza a seção principal de preview de Excel"""
        st.markdown("### 📁 **Upload e Pré-visualização de Planilhas Excel**")
        st.markdown("Faça upload de arquivos Excel (.xlsx ou .xls) para visualizar rapidamente seu conteúdo com navegação entre abas.")
        
        # Upload de arquivo
        uploaded_file = st.file_uploader(
            "Selecione seu arquivo Excel",
            type=["xlsx", "xls"],
            help="Formatos aceitos: .xlsx e .xls",
            key="main_excel_uploader"
        )
        
        if uploaded_file is not None:
            self._process_uploaded_file(uploaded_file)
        else:
            self._render_upload_placeholder()
    
    def _process_uploaded_file(self, uploaded_file):
        """Processa e exibe o arquivo Excel carregado"""
        try:
            # Ler todas as abas do arquivo Excel
            excel_file = pd.ExcelFile(uploaded_file)
            sheet_names = excel_file.sheet_names
            
            # Informações básicas do arquivo
            col1, col2, col3 = st.columns(3)
            with col1:
                st.success(f"✅ **Arquivo:** {uploaded_file.name}")
            with col2:
                st.info(f"📄 **Abas:** {len(sheet_names)}")
            with col3:
                file_size = len(uploaded_file.getvalue()) / 1024  # KB
                st.info(f"📏 **Tamanho:** {file_size:.1f} KB")
            
            # Seletor de abas
            if len(sheet_names) > 1:
                st.markdown("### 📑 **Navegação entre Abas**")
                
                # Criar tabs do Streamlit para navegação
                tabs = st.tabs(sheet_names)
                
                for i, sheet_name in enumerate(sheet_names):
                    with tabs[i]:
                        self._render_sheet_content(excel_file, sheet_name)
            else:
                # Arquivo com uma única aba
                st.markdown("### 📄 **Conteúdo da Planilha**")
                self._render_sheet_content(excel_file, sheet_names[0])
                
        except Exception as e:
            st.error(f"❌ **Erro ao processar arquivo:** {str(e)}")
            st.info("💡 **Dicas:**")
            st.markdown("""
            - Verifique se o arquivo está no formato Excel (.xlsx ou .xls)
            - Certifique-se de que o arquivo não está corrompido
            - Tente com um arquivo menor se estiver muito grande
            """)
    
    def _render_sheet_content(self, excel_file, sheet_name):
        """Renderiza o conteúdo de uma aba específica"""
        try:
            # Ler dados da aba
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            
            # Informações da aba
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📏 Linhas", f"{df.shape[0]:,}")
            with col2:
                st.metric("📊 Colunas", f"{df.shape[1]:,}")
            with col3:
                numeric_cols = len(df.select_dtypes(include=['number']).columns)
                st.metric("🔢 Numéricas", numeric_cols)
            with col4:
                text_cols = len(df.select_dtypes(include=['object']).columns)
                st.metric("📝 Texto", text_cols)
            
            # Controles de visualização
            col1, col2 = st.columns([2, 1])
            with col1:
                max_rows = st.slider(
                    "Número de linhas para visualizar", 
                    min_value=5, 
                    max_value=min(100, len(df)), 
                    value=min(20, len(df)),
                    key=f"rows_slider_{sheet_name}"
                )
            with col2:
                show_info = st.checkbox("Mostrar informações das colunas", key=f"info_check_{sheet_name}")
            
            # Visualização principal dos dados
            st.markdown(f"**Primeiras {max_rows} linhas da aba '{sheet_name}':**")
            
            # Limitar colunas se houver muitas
            max_cols = 50
            if df.shape[1] > max_cols:
                df_display = df.iloc[:max_rows, :max_cols]
                st.warning(f"⚠️ Exibindo apenas as primeiras {max_cols} colunas (arquivo tem {df.shape[1]} colunas)")
            else:
                df_display = df.head(max_rows)
            
            # Exibir dataframe com configurações otimizadas
            st.dataframe(
                df_display,
                use_container_width=True,
                height=400
            )
            
            # Informações detalhadas das colunas (opcional)
            if show_info:
                self._render_column_info(df, sheet_name)
            
            # Estatísticas para colunas numéricas
            numeric_df = df.select_dtypes(include=['number'])
            if len(numeric_df.columns) > 0:
                with st.expander(f"📊 Estatísticas Descritivas - {sheet_name}", expanded=False):
                    st.dataframe(
                        numeric_df.describe().round(2),
                        use_container_width=True
                    )
            
            # Opção de download dos dados filtrados
            if st.button(f"💾 Baixar dados da aba '{sheet_name}' (CSV)", key=f"download_{sheet_name}"):
                csv = df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label=f"📥 Download {sheet_name}.csv",
                    data=csv,
                    file_name=f"{sheet_name}.csv",
                    mime="text/csv",
                    key=f"download_btn_{sheet_name}"
                )
                
        except Exception as e:
            st.error(f"❌ Erro ao processar aba '{sheet_name}': {str(e)}")
    
    def _render_column_info(self, df, sheet_name):
        """Renderiza informações detalhadas das colunas"""
        st.markdown("#### 📋 **Informações das Colunas**")
        
        col_info = []
        for col in df.columns:
            col_type = str(df[col].dtype)
            non_null = df[col].notna().sum()
            null_count = df[col].isna().sum()
            unique_count = df[col].nunique()
            
            col_info.append({
                'Coluna': col,
                'Tipo': col_type,
                'Não Nulos': f"{non_null:,}",
                'Nulos': f"{null_count:,}",
                'Únicos': f"{unique_count:,}",
                'Completude': f"{(non_null/len(df)*100):.1f}%"
            })
        
        col_df = pd.DataFrame(col_info)
        st.dataframe(col_df, use_container_width=True, hide_index=True)
    
    def _render_upload_placeholder(self):
        """Renderiza placeholder quando nenhum arquivo foi carregado"""
        st.markdown("---")
        
        # Área de instruções
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div style="text-align: center; padding: 2rem; border: 2px dashed #cccccc; border-radius: 10px; background-color: #f8f9fa;">
                <h3>📁 Faça Upload de um Arquivo Excel</h3>
                <p>Arraste e solte ou clique para selecionar</p>
                <p style="font-size: 0.9em; color: #666;">Formatos suportados: .xlsx, .xls</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Recursos da página
        st.markdown("### 🚀 **Recursos Disponíveis**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **📊 Visualização:**
            - Preview instantâneo dos dados
            - Navegação entre múltiplas abas
            - Controle de linhas exibidas
            - Informações detalhadas das colunas
            """)
        
        with col2:
            st.markdown("""
            **📈 Análise:**
            - Estatísticas descritivas automáticas
            - Contagem de dados nulos/únicos
            - Identificação de tipos de dados
            - Download em formato CSV
            """)
        
        # Exemplo de uso
        with st.expander("💡 **Como usar**", expanded=False):
            st.markdown("""
            1. **Upload:** Clique em "Browse files" ou arraste seu arquivo Excel
            2. **Navegação:** Use as abas para navegar entre planilhas (se houver múltiplas)
            3. **Visualização:** Ajuste o número de linhas com o slider
            4. **Análise:** Marque "Mostrar informações das colunas" para detalhes
            5. **Download:** Use o botão de download para salvar dados em CSV
            """)
    
    def render_sidebar_info(self):
        """Renderiza informações na sidebar"""
        with st.sidebar:
            st.markdown("### 📊 **Página Indicadores**")
            st.info("Esta página permite fazer upload e visualizar rapidamente planilhas Excel com navegação entre abas.")
            
            st.markdown("---")
            
            # Informações dos dados carregados no app (se houver)
            if hasattr(self, 'df') and self.df is not None and not self.df.empty:
                st.markdown("### 📈 **Dados do Sistema**")
                if hasattr(self.df, 'Ano'):  # Dados financeiros
                    anos = self.df['Ano'].unique()
                    st.success(f"✅ **{len(anos)} anos** de dados financeiros")
                    st.info(f"📅 **Anos:** {', '.join(map(str, sorted(anos)))}")
                else:  # Dados contábeis
                    total_records = len(self.df)
                    st.success(f"✅ **{total_records:,}** registros")
            
            st.markdown("---")
            
            # Dicas rápidas
            st.markdown("### 💡 **Dicas**")
            st.markdown("""
            - **Formatos aceitos:** .xlsx, .xls
            - **Tamanho máximo:** Recomendado até 10MB
            - **Abas múltiplas:** Navegação automática por tabs
            - **Performance:** Use o controle de linhas para arquivos grandes
            """)
