#!/usr/bin/env python3
"""
Script de teste detalhado para a API do Google Gemini
"""

import os
import sys
import traceback
import pandas as pd
from datetime import datetime, timedelta
import random

def test_environment():
    """
    Testa o ambiente e dependências
    """
    print("🔍 Testando ambiente...")
    
    try:
        from dotenv import load_dotenv
        import google.generativeai as genai
        import json
        print("✅ Todas as dependências importadas com sucesso")
        return True
    except ImportError as e:
        print(f"❌ Erro ao importar dependências: {e}")
        return False

def test_env_config():
    """
    Testa a configuração do arquivo .env
    """
    print("\n🔍 Testando configuração...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('GOOGLE_GEMINI_API_KEY')
        
        if not api_key:
            print("❌ API Key não encontrada no .env")
            return False, None
            
        if api_key == 'your_api_key_here':
            print("❌ API Key não foi alterada do exemplo")
            return False, None
            
        print("✅ API Key encontrada e configurada")
        return True, api_key
        
    except Exception as e:
        print(f"❌ Erro ao carregar configuração: {e}")
        return False, None

def test_api_connection(api_key):
    """
    Testa a conexão básica com a API
    """
    print("\n🔍 Testando conexão com API...")
    
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Teste simples
        response = model.generate_content("Responda apenas: 'Conexão OK'")
        
        if response.text:
            print(f"✅ Conexão estabelecida: {response.text}")
            return True, model
        else:
            print("❌ API não retornou resposta")
            return False, None
            
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        print("📋 Detalhes do erro:")
        traceback.print_exc()
        return False, None

def create_test_data():
    """
    Cria dados de teste similares ao app principal
    """
    print("\n📊 Criando dados de teste...")
    
    # Dados simples para teste
    data_fim = datetime.now()
    data_inicio = data_fim - timedelta(days=30)
    
    dados = []
    for i in range(10):
        data = data_inicio + timedelta(days=random.randint(0, 30))
        tipo = random.choice(['Receita', 'Despesa'])
        categoria = random.choice(['Vendas', 'Marketing', 'Salários'])
        valor = round(random.uniform(1000, 10000), 2)
        
        dados.append({
            'Data': data,
            'Descrição': f'Transação {i+1}',
            'Categoria': categoria,
            'Tipo': tipo,
            'Valor': valor
        })
    
    df = pd.DataFrame(dados)
    print(f"✅ Dados criados: {len(df)} registros")
    return df

def test_data_conversion():
    """
    Testa a conversão de dados para JSON
    """
    print("\n🔍 Testando conversão de dados...")
    
    try:
        # Importar nossa classe
        from ai_analyzer import AIAnalyzer
        
        analyzer = AIAnalyzer()
        
        # Criar dados de teste
        df = create_test_data()
        
        # Criar KPIs simples
        kpis = {
            'receita_total': 50000.0,
            'despesa_total': 30000.0,
            'saldo': 20000.0
        }
        
        # Testar conversão
        context = analyzer.prepare_data_context(df, df, kpis)
        
        # Testar se pode ser convertido para JSON
        import json
        json_str = json.dumps(context, indent=2, ensure_ascii=False)
        
        print("✅ Conversão para JSON bem-sucedida")
        print(f"📏 Tamanho do JSON: {len(json_str)} caracteres")
        
        return True, context
        
    except Exception as e:
        print(f"❌ Erro na conversão: {e}")
        print("📋 Detalhes do erro:")
        traceback.print_exc()
        return False, None

def test_ai_analysis(model, context):
    """
    Testa a análise com IA
    """
    print("\n🤖 Testando análise com IA...")
    
    try:
        import json
        
        # Prompt simples para teste
        prompt = f"""
        Você é um analista financeiro. Analise os dados fornecidos e forneça um resumo breve.
        
        DADOS:
        {json.dumps(context, indent=2, ensure_ascii=False)}
        
        Forneça apenas um parágrafo resumindo os dados em português.
        """
        
        print("📤 Enviando prompt para IA...")
        response = model.generate_content(prompt)
        
        if response.text:
            print("✅ Resposta recebida com sucesso!")
            print(f"📝 Resposta: {response.text[:200]}...")
            return True
        else:
            print("❌ IA não retornou resposta")
            return False
            
    except Exception as e:
        print(f"❌ Erro na análise: {e}")
        print("📋 Detalhes do erro:")
        traceback.print_exc()
        return False

def main():
    """
    Função principal de teste
    """
    print("=" * 60)
    print("🧪 Teste Detalhado da API Google Gemini")
    print("=" * 60)
    
    # Teste 1: Ambiente
    if not test_environment():
        print("\n❌ Falha no teste de ambiente")
        return False
    
    # Teste 2: Configuração
    config_ok, api_key = test_env_config()
    if not config_ok:
        print("\n❌ Falha na configuração")
        print("💡 Dicas:")
        print("1. Crie um arquivo .env na raiz do projeto")
        print("2. Adicione: GOOGLE_GEMINI_API_KEY=sua_chave_aqui")
        print("3. Obtenha a chave em: https://makersuite.google.com/app/apikey")
        return False
    
    # Teste 3: Conexão
    connection_ok, model = test_api_connection(api_key)
    if not connection_ok:
        print("\n❌ Falha na conexão")
        return False
    
    # Teste 4: Conversão de dados
    conversion_ok, context = test_data_conversion()
    if not conversion_ok:
        print("\n❌ Falha na conversão de dados")
        return False
    
    # Teste 5: Análise com IA
    analysis_ok = test_ai_analysis(model, context)
    if not analysis_ok:
        print("\n❌ Falha na análise com IA")
        return False
    
    print("\n🎉 Todos os testes passaram com sucesso!")
    print("✅ A API está funcionando corretamente")
    print("🚀 Você pode usar o dashboard normalmente")
    
    return True

if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n💡 Sugestões para resolver problemas:")
        print("1. Verifique se todas as dependências estão instaladas")
        print("2. Confirme se a API key está correta no arquivo .env")
        print("3. Teste sua conexão com a internet")
        print("4. Verifique se não excedeu os limites da API gratuita")
        
    sys.exit(0 if success else 1)
