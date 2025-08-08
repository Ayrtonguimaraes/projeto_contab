"""
Módulo para gerenciar e centralizar todos os gráficos do dashboard
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

class ChartManager:
    """
    Classe para gerenciar todos os gráficos disponíveis no dashboard
    """
    
    def __init__(self):
        self.charts = {
            "evolucao_temporal": {
                "name": "Evolução Temporal (Receitas vs Despesas)",
                "description": "Gráfico de linhas mostrando a evolução das receitas e despesas ao longo do tempo",
                "function": self.create_evolucao_temporal,
                "icon": "📈"
            },
            "despesas_categoria": {
                "name": "Top Despesas por Categoria", 
                "description": "Gráfico de barras horizontais com as principais categorias de despesa",
                "function": self.create_despesas_categoria,
                "icon": "📊"
            },
            "distribuicao_receitas": {
                "name": "Distribuição de Receitas por Categoria",
                "description": "Gráfico de pizza mostrando a distribuição percentual das receitas",
                "function": self.create_distribuicao_receitas,
                "icon": "🥧"
            },
            "distribuicao_despesas": {
                "name": "Distribuição de Despesas por Categoria", 
                "description": "Gráfico de pizza mostrando a distribuição percentual das despesas",
                "function": self.create_distribuicao_despesas,
                "icon": "🥧"
            },
            "comparativo_mensal": {
                "name": "Comparativo Mensal (Saldo)",
                "description": "Gráfico de barras mostrando o saldo (lucro/prejuízo) por mês",
                "function": self.create_comparativo_mensal,
                "icon": "📊"
            }
        }
    
    def get_available_charts(self):
        """
        Retorna lista de gráficos disponíveis para o dropdown
        """
        return [
            f"{chart['icon']} {chart['name']}" 
            for key, chart in self.charts.items()
        ]
    
    def get_chart_key_from_display(self, display_name):
        """
        Converte nome de exibição para chave interna
        """
        for key, chart in self.charts.items():
            if f"{chart['icon']} {chart['name']}" == display_name:
                return key
        return None
    
    def get_chart_info(self, chart_key):
        """
        Retorna informações do gráfico
        """
        return self.charts.get(chart_key, {})
    
    def create_chart_thumbnail(self, chart_key, df_filtrado, container_width=400, container_height=300):
        """
        Cria uma versão miniatura do gráfico
        """
        if chart_key not in self.charts:
            return None
            
        chart_info = self.charts[chart_key]
        
        # Criar o gráfico em tamanho reduzido
        fig = chart_info["function"](df_filtrado, thumbnail=True)
        
        if fig:
            # Configurar tamanho reduzido
            fig.update_layout(
                width=container_width,
                height=container_height,
                margin=dict(l=20, r=20, t=40, b=20),
                font_size=10,
                title_font_size=12,
                showlegend=True,
                legend=dict(font_size=8)
            )
            
        return fig
    
    def create_chart_full(self, chart_key, df_filtrado):
        """
        Cria versão completa do gráfico para análise
        """
        if chart_key not in self.charts:
            return None
            
        chart_info = self.charts[chart_key]
        return chart_info["function"](df_filtrado, thumbnail=False)
    
    def create_evolucao_temporal(self, df_filtrado, thumbnail=False):
        """
        Cria gráfico de evolução temporal
        """
        if df_filtrado.empty:
            return None
            
        # Agrupar por mês e tipo
        df_filtrado['Mes'] = df_filtrado['Data'].dt.to_period('M')
        evolucao_mensal = df_filtrado.groupby(['Mes', 'Tipo'])['Valor'].sum().reset_index()
        evolucao_mensal['Mes'] = evolucao_mensal['Mes'].astype(str)
        
        # Criar gráfico
        fig = px.line(
            evolucao_mensal,
            x='Mes',
            y='Valor',
            color='Tipo',
            title='Evolução Temporal - Receitas vs Despesas',
            labels={'Valor': 'Valor (R$)', 'Mes': 'Mês'},
            color_discrete_map={'Receita': '#2E8B57', 'Despesa': '#DC143C'}
        )
        
        fig.update_layout(
            xaxis_title="Período",
            yaxis_title="Valor (R$)",
            yaxis_tickformat=',.0f'
        )
        
        return fig
    
    def create_despesas_categoria(self, df_filtrado, thumbnail=False):
        """
        Cria gráfico de despesas por categoria
        """
        despesas = df_filtrado[df_filtrado['Tipo'] == 'Despesa']
        
        if despesas.empty:
            return None
            
        despesas_por_categoria = despesas.groupby('Categoria')['Valor'].sum().sort_values(ascending=True)
        
        fig = px.bar(
            x=despesas_por_categoria.values,
            y=despesas_por_categoria.index,
            orientation='h',
            title='Top Despesas por Categoria',
            labels={'x': 'Valor (R$)', 'y': 'Categoria'},
            color=despesas_por_categoria.values,
            color_continuous_scale='Reds'
        )
        
        fig.update_layout(
            xaxis_title="Valor (R$)",
            yaxis_title="Categoria",
            xaxis_tickformat=',.0f',
            showlegend=False
        )
        
        return fig
    
    def create_distribuicao_receitas(self, df_filtrado, thumbnail=False):
        """
        Cria gráfico de distribuição de receitas
        """
        receitas = df_filtrado[df_filtrado['Tipo'] == 'Receita']
        
        if receitas.empty:
            return None
            
        distribuicao = receitas.groupby('Categoria')['Valor'].sum().sort_values(ascending=False)
        
        fig = px.pie(
            values=distribuicao.values,
            names=distribuicao.index,
            title='Distribuição de Receitas por Categoria',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
        return fig
    
    def create_distribuicao_despesas(self, df_filtrado, thumbnail=False):
        """
        Cria gráfico de distribuição de despesas
        """
        despesas = df_filtrado[df_filtrado['Tipo'] == 'Despesa']
        
        if despesas.empty:
            return None
            
        distribuicao = despesas.groupby('Categoria')['Valor'].sum().sort_values(ascending=False)
        
        fig = px.pie(
            values=distribuicao.values,
            names=distribuicao.index,
            title='Distribuição de Despesas por Categoria',
            color_discrete_sequence=px.colors.qualitative.Set1
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
        return fig
    
    def create_comparativo_mensal(self, df_filtrado, thumbnail=False):
        """
        Cria gráfico de comparativo mensal (saldo)
        """
        if df_filtrado.empty:
            return None
            
        # Calcular saldo por mês
        df_filtrado['Mes'] = df_filtrado['Data'].dt.to_period('M')
        mensal = df_filtrado.groupby(['Mes', 'Tipo'])['Valor'].sum().reset_index()
        
        # Pivot para ter receitas e despesas em colunas separadas
        pivot = mensal.pivot(index='Mes', columns='Tipo', values='Valor').fillna(0)
        
        if 'Receita' in pivot.columns and 'Despesa' in pivot.columns:
            pivot['Saldo'] = pivot['Receita'] - pivot['Despesa']
        else:
            pivot['Saldo'] = pivot.sum(axis=1)
        
        pivot = pivot.reset_index()
        pivot['Mes'] = pivot['Mes'].astype(str)
        
        # Definir cores (verde para positivo, vermelho para negativo)
        colors = ['#2E8B57' if saldo >= 0 else '#DC143C' for saldo in pivot['Saldo']]
        
        fig = px.bar(
            pivot,
            x='Mes',
            y='Saldo',
            title='Saldo Mensal (Lucro/Prejuízo)',
            labels={'Saldo': 'Saldo (R$)', 'Mes': 'Mês'},
            color=pivot['Saldo'],
            color_continuous_scale='RdYlGn',
            color_continuous_midpoint=0
        )
        
        fig.update_layout(
            xaxis_title="Período",
            yaxis_title="Saldo (R$)",
            yaxis_tickformat=',.0f',
            showlegend=False
        )
        
        # Adicionar linha zero
        fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5)
        
        return fig
    
    def get_chart_data_for_ai(self, chart_key, df_filtrado):
        """
        Prepara dados do gráfico específico para análise da IA
        """
        if chart_key == "evolucao_temporal":
            df_filtrado['Mes'] = df_filtrado['Data'].dt.to_period('M')
            return df_filtrado.groupby(['Mes', 'Tipo'])['Valor'].sum().reset_index()
            
        elif chart_key == "despesas_categoria":
            despesas = df_filtrado[df_filtrado['Tipo'] == 'Despesa']
            return despesas.groupby('Categoria')['Valor'].sum().reset_index()
            
        elif chart_key == "distribuicao_receitas":
            receitas = df_filtrado[df_filtrado['Tipo'] == 'Receita']
            return receitas.groupby('Categoria')['Valor'].sum().reset_index()
            
        elif chart_key == "distribuicao_despesas":
            despesas = df_filtrado[df_filtrado['Tipo'] == 'Despesa'] 
            return despesas.groupby('Categoria')['Valor'].sum().reset_index()
            
        elif chart_key == "comparativo_mensal":
            df_filtrado['Mes'] = df_filtrado['Data'].dt.to_period('M')
            mensal = df_filtrado.groupby(['Mes', 'Tipo'])['Valor'].sum().reset_index()
            pivot = mensal.pivot(index='Mes', columns='Tipo', values='Valor').fillna(0)
            if 'Receita' in pivot.columns and 'Despesa' in pivot.columns:
                pivot['Saldo'] = pivot['Receita'] - pivot['Despesa']
            return pivot.reset_index()
            
        return df_filtrado
