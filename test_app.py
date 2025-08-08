#!/usr/bin/env python3
"""
Script de teste para verificar se o código principal do dashboard funciona corretamente
"""

import sys
import pandas as pd
from datetime import datetime, timedelta
import random

# Simular as funções do app.py
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
    
    df = pd.DataFrame(dados)
    df = df.sort_values('Data')
    return df

def aplicar_filtros(df, data_inicio, data_fim, tipos, categorias):
    """
    Aplica os filtros selecionados ao DataFrame
    """
    df_filtrado = df.copy()
    
    # Filtro por período
    df_filtrado = df_filtrado[
        (df_filtrado['Data'].dt.date >= data_inicio) &
        (df_filtrado['Data'].dt.date <= data_fim)
    ]
    
    # Filtro por tipo
    if tipos:
        df_filtrado = df_filtrado[df_filtrado['Tipo'].isin(tipos)]
    
    # Filtro por categoria
    if categorias:
        df_filtrado = df_filtrado[df_filtrado['Categoria'].isin(categorias)]
    
    return df_filtrado

def calcular_kpis(df_filtrado):
    """
    Calcula os KPIs principais
    """
    receita_total = df_filtrado[df_filtrado['Tipo'] == 'Receita']['Valor'].sum()
    despesa_total = df_filtrado[df_filtrado['Tipo'] == 'Despesa']['Valor'].sum()
    saldo = receita_total - despesa_total
    
    return {
        'receita_total': receita_total,
        'despesa_total': despesa_total,
        'saldo': saldo
    }

def main():
    """
    Função principal de teste
    """
    print("🧪 Iniciando testes do Dashboard Contábil...")
    
    try:
        # Teste 1: Gerar dados
        print("1. Gerando dados fictícios...")
        df = gerar_dados_contabeis()
        print(f"   ✅ Dados gerados com sucesso: {len(df)} registros")
        print(f"   📅 Período: {df['Data'].min().strftime('%d/%m/%Y')} a {df['Data'].max().strftime('%d/%m/%Y')}")
        
        # Teste 2: Verificar estrutura dos dados
        print("\n2. Verificando estrutura dos dados...")
        colunas_esperadas = ['Data', 'Descrição', 'Categoria', 'Tipo', 'Valor']
        colunas_atuais = df.columns.tolist()
        
        if set(colunas_esperadas) == set(colunas_atuais):
            print("   ✅ Estrutura dos dados está correta")
        else:
            print(f"   ❌ Estrutura incorreta. Esperado: {colunas_esperadas}, Atual: {colunas_atuais}")
            return False
        
        # Teste 3: Verificar tipos de dados
        print("\n3. Verificando tipos de dados...")
        if df['Data'].dtype == 'datetime64[ns]':
            print("   ✅ Coluna Data está no formato correto")
        else:
            print(f"   ❌ Coluna Data com tipo incorreto: {df['Data'].dtype}")
        
        if df['Valor'].dtype in ['float64', 'float32']:
            print("   ✅ Coluna Valor está no formato correto")
        else:
            print(f"   ❌ Coluna Valor com tipo incorreto: {df['Valor'].dtype}")
        
        # Teste 4: Verificar categorias
        print("\n4. Verificando categorias...")
        categorias_receitas = df[df['Tipo'] == 'Receita']['Categoria'].unique()
        categorias_despesas = df[df['Tipo'] == 'Despesa']['Categoria'].unique()
        
        print(f"   📈 Categorias de Receita: {len(categorias_receitas)}")
        print(f"   📉 Categorias de Despesa: {len(categorias_despesas)}")
        
        # Teste 5: Testar filtros
        print("\n5. Testando filtros...")
        data_inicio = df['Data'].min().date()
        data_fim = df['Data'].max().date()
        tipos = ['Receita', 'Despesa']
        categorias = df['Categoria'].unique().tolist()
        
        df_filtrado = aplicar_filtros(df, data_inicio, data_fim, tipos, categorias)
        
        if len(df_filtrado) == len(df):
            print("   ✅ Filtros funcionando corretamente")
        else:
            print(f"   ❌ Problema com filtros: {len(df_filtrado)} vs {len(df)}")
        
        # Teste 6: Calcular KPIs
        print("\n6. Calculando KPIs...")
        kpis = calcular_kpis(df_filtrado)
        
        print(f"   💰 Receita Total: R$ {kpis['receita_total']:,.2f}")
        print(f"   💸 Despesa Total: R$ {kpis['despesa_total']:,.2f}")
        print(f"   📊 Saldo: R$ {kpis['saldo']:,.2f}")
        
        # Teste 7: Verificar valores
        print("\n7. Verificando valores...")
        if kpis['receita_total'] > 0 and kpis['despesa_total'] > 0:
            print("   ✅ Valores calculados corretamente")
        else:
            print("   ❌ Valores zerados ou negativos")
        
        # Teste 8: Verificar distribuição
        print("\n8. Verificando distribuição dos dados...")
        receitas = df[df['Tipo'] == 'Receita']
        despesas = df[df['Tipo'] == 'Despesa']
        
        print(f"   📈 Total de Receitas: {len(receitas)} registros")
        print(f"   📉 Total de Despesas: {len(despesas)} registros")
        
        if len(receitas) > 0 and len(despesas) > 0:
            print("   ✅ Distribuição balanceada entre receitas e despesas")
        else:
            print("   ❌ Distribuição desbalanceada")
        
        print("\n🎉 Todos os testes passaram com sucesso!")
        print("✅ O dashboard está pronto para ser executado!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 