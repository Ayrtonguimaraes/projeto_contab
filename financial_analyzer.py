"""
Módulo de Análise Financeira Profissional
Projetado para análise de indicadores contábeis e financeiros
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
import numpy as np

class FinancialAnalyzer:
    def __init__(self, df):
        """
        Inicializa o analisador financeiro com os dados
        """
        self.df = df
        self.prepare_data()
    
    def prepare_data(self):
        """
        Prepara e limpa os dados para análise
        """
        print("Iniciando preparação dos dados...")
        print(f"Dados originais - Shape: {self.df.shape}")
        print(f"Colunas: {self.df.columns.tolist()}")
        
        # Converter valores numéricos brasileiros (1.234.567,89) para formato padrão
        numeric_columns = self.df.columns[:-1]  # Todas exceto 'Ano'
        
        for col in numeric_columns:
            print(f"Processando coluna: {col}")
            print(f"Tipo atual: {self.df[col].dtype}")
            print(f"Amostra de valores: {self.df[col].head(3).tolist()}")
            
            if self.df[col].dtype == 'object':
                try:
                    # Tratar formato brasileiro: remover pontos (separador de milhares) e trocar vírgula por ponto
                    self.df[col] = (self.df[col].astype(str)
                                   .str.strip()  # Remove espaços em branco
                                   .str.replace('.', '', regex=False)  # Remove pontos (separador de milhares)
                                   .str.replace(',', '.', regex=False)  # Troca vírgula por ponto (decimal)
                                   .replace(['', 'nan', 'NaN', 'None'], '0')  # Substitui valores vazios por 0
                                   .astype(float))
                    print(f"✅ Coluna {col} convertida com sucesso")
                except (ValueError, TypeError) as e:
                    print(f"❌ Erro ao converter coluna {col}: {e}")
                    # Se falhar, tentar conversão direta
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce').fillna(0)
            else:
                # Se já é numérico, garantir que é float
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce').fillna(0)
        
        # Garantir que Ano seja inteiro
        try:
            self.df['Ano'] = self.df['Ano'].astype(int)
            print(f"✅ Coluna 'Ano' convertida para int")
        except:
            # Se falhar, tentar limpeza primeiro
            self.df['Ano'] = pd.to_numeric(self.df['Ano'], errors='coerce').fillna(2024).astype(int)
            print(f"⚠️ Coluna 'Ano' convertida com fallback")
        
        # Ordenar por ano
        self.df = self.df.sort_values('Ano')
        
        print("✅ Preparação dos dados concluída!")
        print(f"Dados finais - Shape: {self.df.shape}")
        print(f"Tipos de dados:")
        for col in self.df.columns:
            print(f"  {col}: {self.df[col].dtype}")
        print("="*50)
    
    def get_kpis_principais(self):
        """
        Calcula e retorna os KPIs principais
        """
        ano_atual = self.df['Ano'].max()
        ano_anterior = self.df['Ano'].min()
        
        dados_atual = self.df[self.df['Ano'] == ano_atual].iloc[0]
        dados_anterior = self.df[self.df['Ano'] == ano_anterior].iloc[0]
        
        def calcular_variacao(atual, anterior):
            if anterior != 0:
                return ((atual - anterior) / anterior) * 100
            return 0
        
        kpis = {
            'receita_liquida': {
                'atual': dados_atual['Receita Líquida'],
                'anterior': dados_anterior['Receita Líquida'],
                'variacao': calcular_variacao(dados_atual['Receita Líquida'], dados_anterior['Receita Líquida'])
            },
            'lucro_liquido': {
                'atual': dados_atual['Lucro Líquido'],
                'anterior': dados_anterior['Lucro Líquido'],
                'variacao': calcular_variacao(dados_atual['Lucro Líquido'], dados_anterior['Lucro Líquido'])
            },
            'roe': {
                'atual': dados_atual['Rentabilidade do Patrimônio Líquido (ROE) '],
                'anterior': dados_anterior['Rentabilidade do Patrimônio Líquido (ROE) '],
                'variacao': calcular_variacao(dados_atual['Rentabilidade do Patrimônio Líquido (ROE) '], 
                                           dados_anterior['Rentabilidade do Patrimônio Líquido (ROE) '])
            },
            'roa': {
                'atual': dados_atual['Rentabilidade do Ativo (ROA ou ROI)'],
                'anterior': dados_anterior['Rentabilidade do Ativo (ROA ou ROI)'],
                'variacao': calcular_variacao(dados_atual['Rentabilidade do Ativo (ROA ou ROI)'], 
                                           dados_anterior['Rentabilidade do Ativo (ROA ou ROI)'])
            },
            'margem_liquida': {
                'atual': dados_atual['Margem Líquida (ML)'],
                'anterior': dados_anterior['Margem Líquida (ML)'],
                'variacao': calcular_variacao(dados_atual['Margem Líquida (ML)'], 
                                           dados_anterior['Margem Líquida (ML)'])
            },
            'liquidez_corrente': {
                'atual': dados_atual['Liquidez Corrente (LC) '],
                'anterior': dados_anterior['Liquidez Corrente (LC) '],
                'variacao': calcular_variacao(dados_atual['Liquidez Corrente (LC) '], 
                                           dados_anterior['Liquidez Corrente (LC) '])
            }
        }
        
        return kpis
    
    def create_rentabilidade_chart(self):
        """
        Gráfico de Análise de Rentabilidade (ROA, ROE, Margem Líquida)
        """
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('ROE - Rentabilidade do Patrimônio', 'ROA - Rentabilidade do Ativo', 
                          'Margem Líquida', 'Comparativo de Rentabilidade'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        anos = self.df['Ano'].tolist()
        roe = self.df['Rentabilidade do Patrimônio Líquido (ROE) '].tolist()
        roa = self.df['Rentabilidade do Ativo (ROA ou ROI)'].tolist()
        margem = self.df['Margem Líquida (ML)'].tolist()
        
        # ROE
        fig.add_trace(
            go.Scatter(x=anos, y=roe, mode='lines+markers', name='ROE', 
                      line=dict(color='#1f77b4', width=3), marker=dict(size=10)),
            row=1, col=1
        )
        
        # ROA
        fig.add_trace(
            go.Scatter(x=anos, y=roa, mode='lines+markers', name='ROA',
                      line=dict(color='#ff7f0e', width=3), marker=dict(size=10)),
            row=1, col=2
        )
        
        # Margem Líquida
        fig.add_trace(
            go.Scatter(x=anos, y=margem, mode='lines+markers', name='Margem Líquida',
                      line=dict(color='#2ca02c', width=3), marker=dict(size=10)),
            row=2, col=1
        )
        
        # Comparativo
        fig.add_trace(
            go.Scatter(x=anos, y=roe, mode='lines+markers', name='ROE',
                      line=dict(color='#1f77b4', width=2)),
            row=2, col=2
        )
        fig.add_trace(
            go.Scatter(x=anos, y=roa, mode='lines+markers', name='ROA',
                      line=dict(color='#ff7f0e', width=2)),
            row=2, col=2
        )
        fig.add_trace(
            go.Scatter(x=anos, y=margem, mode='lines+markers', name='Margem Líquida',
                      line=dict(color='#2ca02c', width=2)),
            row=2, col=2
        )
        
        fig.update_layout(
            title="📈 Análise de Rentabilidade",
            height=600,
            showlegend=False
        )
        
        return fig
    
    def create_liquidez_radar(self):
        """
        Gráfico Radar dos Indicadores de Liquidez
        """
        anos = self.df['Ano'].tolist()
        
        # Indicadores de liquidez
        indicators = ['Liquidez Geral (LG)', 'Liquidez Corrente (LC) ', 
                     'Liquidez Seca (LS)', 'Liquidez Imediata (LI)']
        
        fig = go.Figure()
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        
        for i, ano in enumerate(anos):
            valores = []
            for indicator in indicators:
                valores.append(self.df[self.df['Ano'] == ano][indicator].iloc[0])
            
            # Adicionar o primeiro valor no final para fechar o radar
            valores.append(valores[0])
            labels = [ind.replace(' (', '<br>(').replace(') ', ')') for ind in indicators]
            labels.append(labels[0])
            
            fig.add_trace(go.Scatterpolar(
                r=valores,
                theta=labels,
                fill='toself',
                name=f'Ano {ano}',
                line=dict(color=colors[i], width=3),
                marker=dict(size=8)
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max([self.df[ind].max() for ind in indicators]) * 1.1]
                )
            ),
            showlegend=True,
            title="🛡️ Radar de Indicadores de Liquidez",
            height=500
        )
        
        return fig
    
    def create_estrutura_capital(self):
        """
        Análise da Estrutura de Capital
        """
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Endividamento Geral', 'Composição do Endividamento', 
                          'Participação de Terceiros', 'Evolução da Estrutura'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "scatter"}]]
        )
        
        anos = self.df['Ano'].tolist()
        
        # Endividamento Geral
        eg = self.df['Endividamento Geral (EG)'].tolist()
        fig.add_trace(
            go.Bar(x=anos, y=eg, name='Endividamento Geral', 
                   marker_color='#ff6b6b'),
            row=1, col=1
        )
        
        # Composição do Endividamento
        ce = self.df['Composição do Endividamento (CE)'].tolist()
        fig.add_trace(
            go.Bar(x=anos, y=ce, name='Composição Endividamento',
                   marker_color='#4ecdc4'),
            row=1, col=2
        )
        
        # Participação de Capitais de Terceiros
        pct = self.df['Participação de Capitais de Terceiros (PCT) – Grau de Endividamento'].tolist()
        fig.add_trace(
            go.Bar(x=anos, y=pct, name='PCT',
                   marker_color='#45b7d1'),
            row=2, col=1
        )
        
        # Evolução conjunta
        fig.add_trace(
            go.Scatter(x=anos, y=eg, mode='lines+markers', name='Endividamento Geral',
                      line=dict(color='#ff6b6b', width=3)),
            row=2, col=2
        )
        fig.add_trace(
            go.Scatter(x=anos, y=ce, mode='lines+markers', name='Composição',
                      line=dict(color='#4ecdc4', width=3)),
            row=2, col=2
        )
        
        fig.update_layout(
            title="🏦 Análise da Estrutura de Capital",
            height=600,
            showlegend=False
        )
        
        return fig
    
    def create_evolucao_patrimonial(self):
        """
        Gráfico de Evolução Patrimonial
        """
        fig = go.Figure()
        
        anos = self.df['Ano'].tolist()
        ativo_total = self.df['Ativo Total'].tolist()
        patrimonio_liquido = self.df['Patrimônio Líquido'].tolist()
        passivo_circulante = self.df['Passivo Circulante'].tolist()
        passivo_nao_circulante = self.df['Passivo Não Circulante'].tolist()
        
        fig.add_trace(go.Scatter(
            x=anos, y=ativo_total,
            mode='lines+markers',
            name='Ativo Total',
            line=dict(color='#1f77b4', width=4),
            marker=dict(size=12)
        ))
        
        fig.add_trace(go.Scatter(
            x=anos, y=patrimonio_liquido,
            mode='lines+markers',
            name='Patrimônio Líquido',
            line=dict(color='#2ca02c', width=4),
            marker=dict(size=12)
        ))
        
        fig.add_trace(go.Scatter(
            x=anos, y=passivo_circulante,
            mode='lines+markers',
            name='Passivo Circulante',
            line=dict(color='#ff7f0e', width=3),
            marker=dict(size=10)
        ))
        
        fig.add_trace(go.Scatter(
            x=anos, y=passivo_nao_circulante,
            mode='lines+markers',
            name='Passivo Não Circulante',
            line=dict(color='#d62728', width=3),
            marker=dict(size=10)
        ))
        
        fig.update_layout(
            title="💰 Evolução Patrimonial",
            xaxis_title="Ano",
            yaxis_title="Valor (R$)",
            height=500,
            hovermode='x unified'
        )
        
        return fig
    
    def create_analise_dupont(self):
        """
        Análise DuPont - Decomposição do ROA
        """
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Margem Líquida vs Giro do Ativo', 'ROA vs ROE', 
                          'Multiplicador de Alavancagem', 'Decomposição DuPont'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        anos = self.df['Ano'].tolist()
        margem = self.df['Margem Líquida (ML)'].tolist()
        giro = self.df['Giro do Ativo (GA)'].tolist()
        roa = self.df['Rentabilidade do Ativo (ROA ou ROI)'].tolist()
        roe = self.df['Rentabilidade do Patrimônio Líquido (ROE) '].tolist()
        maf = self.df['Multiplicador de Alavancagem Financeira (MAF)'].tolist()
        
        # Margem vs Giro
        fig.add_trace(
            go.Scatter(x=margem, y=giro, mode='markers+text', 
                      text=[str(ano) for ano in anos],
                      textposition="middle right",
                      marker=dict(size=15, color=anos, colorscale='viridis'),
                      name='Margem vs Giro'),
            row=1, col=1
        )
        
        # ROA vs ROE
        fig.add_trace(
            go.Scatter(x=roa, y=roe, mode='markers+text',
                      text=[str(ano) for ano in anos],
                      textposition="middle right",
                      marker=dict(size=15, color=anos, colorscale='plasma'),
                      name='ROA vs ROE'),
            row=1, col=2
        )
        
        # Multiplicador de Alavancagem
        fig.add_trace(
            go.Bar(x=anos, y=maf, name='Multiplicador Alavancagem',
                   marker_color='#ff9999'),
            row=2, col=1
        )
        
        # Decomposição DuPont (ROA = Margem × Giro)
        roa_calculado = [m * g for m, g in zip(margem, giro)]
        fig.add_trace(
            go.Scatter(x=anos, y=roa, mode='lines+markers', name='ROA Real',
                      line=dict(color='#1f77b4', width=3)),
            row=2, col=2
        )
        fig.add_trace(
            go.Scatter(x=anos, y=roa_calculado, mode='lines+markers', name='ROA Calculado',
                      line=dict(color='#ff7f0e', width=3, dash='dash')),
            row=2, col=2
        )
        
        fig.update_layout(
            title="🔍 Análise DuPont - Decomposição da Rentabilidade",
            height=700,
            showlegend=False
        )
        
        return fig
    
    def create_ciclo_financeiro(self):
        """
        Análise do Ciclo Operacional e Financeiro
        """
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Prazos Médios (dias)', 'Ciclo Operacional vs Financeiro')
        )
        
        anos = self.df['Ano'].tolist()
        pmre = self.df['Prazo Médio de Renovação dos Estoques (PMRE) '].tolist()
        pmrv = self.df['Prazo Médio de Recebimento das Vendas (PMRV) '].tolist()
        pmpc = self.df['Prazo Médio de Pagamento das Compras (PMPC) '].tolist()
        ciclo = self.df['Ciclo Operacional e Ciclo Financeiro'].tolist()
        
        # Prazos médios
        fig.add_trace(
            go.Bar(x=anos, y=pmre, name='PMRE - Estoques', marker_color='#ff9999'),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(x=anos, y=pmrv, name='PMRV - Recebimento', marker_color='#66b3ff'),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(x=anos, y=pmpc, name='PMPC - Pagamento', marker_color='#99ff99'),
            row=1, col=1
        )
        
        # Ciclo Financeiro
        ciclo_operacional = [pmre_val + pmrv_val for pmre_val, pmrv_val in zip(pmre, pmrv)]
        
        fig.add_trace(
            go.Scatter(x=anos, y=ciclo_operacional, mode='lines+markers', 
                      name='Ciclo Operacional', line=dict(color='#1f77b4', width=4)),
            row=1, col=2
        )
        fig.add_trace(
            go.Scatter(x=anos, y=ciclo, mode='lines+markers',
                      name='Ciclo Financeiro', line=dict(color='#ff7f0e', width=4)),
            row=1, col=2
        )
        
        fig.update_layout(
            title="⏱️ Análise do Ciclo Operacional e Financeiro",
            height=500
        )
        
        return fig
    
    def create_heatmap_indicadores(self):
        """
        Heatmap de todos os indicadores para análise comparativa
        """
        # Selecionar indicadores principais para o heatmap
        indicadores_selecionados = [
            'Liquidez Geral (LG)', 'Liquidez Corrente (LC) ', 'Liquidez Seca (LS)',
            'Endividamento Geral (EG)', 'Margem Líquida (ML)', 
            'Rentabilidade do Ativo (ROA ou ROI)', 'Rentabilidade do Patrimônio Líquido (ROE) ',
            'Giro do Ativo (GA)'
        ]
        
        # Preparar dados para heatmap
        heatmap_data = []
        anos = self.df['Ano'].tolist()
        
        for indicador in indicadores_selecionados:
            valores = self.df[indicador].tolist()
            heatmap_data.append(valores)
        
        # Normalizar os dados para melhor visualização
        heatmap_data_norm = []
        for row in heatmap_data:
            if max(row) != min(row):
                normalized = [(x - min(row)) / (max(row) - min(row)) for x in row]
            else:
                normalized = [0.5] * len(row)
            heatmap_data_norm.append(normalized)
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data_norm,
            x=[f'Ano {ano}' for ano in anos],
            y=[ind.replace(' (', '<br>(') for ind in indicadores_selecionados],
            colorscale='RdYlBu_r',
            showscale=True
        ))
        
        fig.update_layout(
            title="🌡️ Heatmap de Indicadores Financeiros (Normalizado)",
            height=600
        )
        
        return fig
    
    def get_data_for_ai(self):
        """
        Prepara dados estruturados para análise da IA
        """
        return {
            'dados_brutos': self.df.to_dict('records'),
            'kpis': self.get_kpis_principais(),
            'anos_analisados': self.df['Ano'].tolist(),
            'total_indicadores': len(self.df.columns) - 1,
            'indicadores_principais': {
                'rentabilidade': ['Rentabilidade do Ativo (ROA ou ROI)', 'Rentabilidade do Patrimônio Líquido (ROE) ', 'Margem Líquida (ML)'],
                'liquidez': ['Liquidez Geral (LG)', 'Liquidez Corrente (LC) ', 'Liquidez Seca (LS)', 'Liquidez Imediata (LI)'],
                'endividamento': ['Endividamento Geral (EG)', 'Participação de Capitais de Terceiros (PCT) – Grau de Endividamento', 'Composição do Endividamento (CE)'],
                'eficiencia': ['Giro do Ativo (GA)', 'Prazo Médio de Renovação dos Estoques (PMRE) ', 'Prazo Médio de Recebimento das Vendas (PMRV) ']
            }
        }
    # ---- LEGACY WRAPPERS (Backward Compatibility) ----
    # Alguns trechos antigos/fallback ainda chamam métodos removidos. 
    # Mantemos aliases para evitar quebras até completa remoção do código legado.
    def create_liquidez_chart(self):
        return self.create_liquidez_radar()
    def create_endividamento_chart(self):
        return self.create_estrutura_capital()
    def create_ciclo_chart(self):
        return self.create_ciclo_financeiro()
    def create_heatmap_geral(self):
        return self.create_heatmap_indicadores()
