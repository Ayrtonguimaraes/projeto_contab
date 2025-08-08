"""
Módulo para carregar e gerar dados
"""

import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import random
from config.settings import AppConfig

def carregar_dados_financeiros():
    """
    Carrega os dados financeiros do arquivo CSV
    """
    try:
        config = AppConfig.DATA_CONFIG
        df = pd.read_csv(
            config["csv_file"], 
            sep=config["separator"], 
            decimal=config["decimal"]
        )
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        # Retorna dados de exemplo se houver erro
        return pd.DataFrame({
            'Ativo Total': [1124797, 1050888],
            'Receita Líquida': [490829, 511994],
            'Lucro Líquido': [37009, 125166],
            'Rentabilidade do Ativo (ROA ou ROI)': [0.03, 0.12],
            'Rentabilidade do Patrimônio Líquido (ROE) ': [0.10, 0.33],
            'Liquidez Corrente (LC) ': [0.69, 0.96],
            'Endividamento Geral (EG)': [0.67, 0.64],
            'Ano': [2024, 2023]
        })

def gerar_dados_contabeis():
    """
    Gera dados fictícios para simular um livro contábil
    """
    # Configuração de datas (últimos 18 meses)
    data_fim = datetime.now()
    data_inicio = data_fim - timedelta(days=18*30)
    
    # Categorias de transações
    categorias_despesas = [
        'Salários', 'Marketing', 'Infraestrutura', 'Software', 
        'Impostos', 'Fornecedores', 'Aluguel', 'Energia', 'Internet'
    ]
    
    categorias_receitas = [
        'Venda de Produtos', 'Serviços Prestados', 'Consultoria',
        'Licenciamento', 'Royalties', 'Investimentos'
    ]
    
    # Dados para gerar transações
    dados = []
    
    for _ in range(200):
        # Data aleatória no período
        data = data_inicio + timedelta(
            days=random.randint(0, (data_fim - data_inicio).days)
        )
        
        # Decidir se é receita ou despesa
        tipo = random.choice(['Receita', 'Despesa'])
        
        if tipo == 'Receita':
            categoria = random.choice(categorias_receitas)
            # Valores de receita entre 1000 e 50000
            valor = round(random.uniform(1000, 50000), 2)
            descricoes = [
                f"Venda de {random.choice(['Produto A', 'Produto B', 'Produto C'])}",
                f"Serviço de {random.choice(['Consultoria', 'Desenvolvimento', 'Suporte'])}",
                f"Licenciamento {random.choice(['Software X', 'Patente Y', 'Marca Z'])}",
                f"Royalties {random.choice(['Produto 1', 'Produto 2'])}",
                f"Investimento {random.choice(['Série A', 'Série B'])}"
            ]
        else:
            categoria = random.choice(categorias_despesas)
            # Valores de despesa entre 100 e 15000
            valor = round(random.uniform(100, 15000), 2)
            descricoes = [
                f"Pagamento {random.choice(['Salário', 'Bonus', 'Comissão'])}",
                f"Campanha de {random.choice(['Marketing Digital', 'Publicidade', 'SEO'])}",
                f"Manutenção {random.choice(['Servidor', 'Equipamento', 'Sistema'])}",
                f"Licença {random.choice(['Software', 'Ferramenta', 'Plataforma'])}",
                f"Imposto {random.choice(['ICMS', 'ISS', 'IR'])}",
                f"Fornecedor {random.choice(['Matéria Prima', 'Serviços', 'Equipamentos'])}"
            ]
        
        descricao = random.choice(descricoes)
        
        dados.append({
            'Data': data,
            'Descrição': descricao,
            'Categoria': categoria,
            'Tipo': tipo,
            'Valor': valor
        })
    
    # Criar DataFrame e ordenar por data
    df = pd.DataFrame(dados)
    df = df.sort_values('Data').reset_index(drop=True)
    
    return df

def carregar_dados():
    """
    Função consolidada para carregar dados (financeiros reais ou fictícios)
    """
    # Primeiro tenta carregar dados reais
    try:
        df = carregar_dados_financeiros()
        if df is not None and not df.empty:
            return df
    except Exception:
        pass
    
    # Se falhar, gera dados fictícios
    return gerar_dados_contabeis()
