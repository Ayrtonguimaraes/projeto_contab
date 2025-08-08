#!/usr/bin/env python3
"""
Script simples para verificar se a configuração do Google Gemini está correta
"""

import os
import sys

def check_dependencies():
    """
    Verifica se as dependências estão instaladas
    """
    print("🔍 Verificando dependências...")
    
    missing_deps = []
    
    # Verificar python-dotenv
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv instalado")
    except ImportError:
        missing_deps.append("python-dotenv")
        print("❌ python-dotenv não instalado")
    
    # Verificar google-generativeai
    try:
        import google.generativeai as genai
        print("✅ google-generativeai instalado")
    except ImportError:
        missing_deps.append("google-generativeai")
        print("❌ google-generativeai não instalado")
    
    if missing_deps:
        print(f"\n❌ Dependências faltando: {', '.join(missing_deps)}")
        print("📦 Para instalar, execute:")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def check_env_file():
    """
    Verifica se o arquivo .env existe e tem a API key
    """
    print("\n🔍 Verificando arquivo .env...")
    
    env_file = ".env"
    
    if not os.path.exists(env_file):
        print("❌ Arquivo .env não encontrado!")
        print("\n📋 Para criar:")
        print("1. Copie o arquivo de exemplo:")
        print("   cp config.env.example .env")
        print("2. Edite o arquivo .env e adicione sua API key")
        return False
    
    print("✅ Arquivo .env encontrado!")
    
    # Tentar carregar variáveis de ambiente
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('GOOGLE_GEMINI_API_KEY')
        
        if not api_key:
            print("❌ API key não encontrada no arquivo .env!")
            print("   Adicione: GOOGLE_GEMINI_API_KEY=sua_chave_aqui")
            return False
        
        if api_key == 'your_api_key_here':
            print("❌ API key não foi configurada!")
            print("   Substitua 'your_api_key_here' pela sua chave real")
            return False
        
        print("✅ API key encontrada!")
        return True
        
    except ImportError:
        print("⚠️  Não foi possível verificar a API key (dotenv não instalado)")
        print("   Instale as dependências primeiro")
        return False

def test_api_connection():
    """
    Testa a conexão com a API
    """
    print("\n🧪 Testando conexão com a API...")
    
    try:
        from dotenv import load_dotenv
        import google.generativeai as genai
        
        load_dotenv()
        api_key = os.getenv('GOOGLE_GEMINI_API_KEY')
        
        if not api_key or api_key == 'your_api_key_here':
            print("❌ API key não configurada corretamente")
            return False
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Teste de conexão")
        
        if response.text:
            print("✅ Conexão com a API estabelecida com sucesso!")
            print(f"🤖 Resposta: {response.text}")
            return True
        else:
            print("❌ API não retornou resposta válida")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar API: {e}")
        return False

def main():
    """
    Função principal
    """
    print("=" * 60)
    print("🤖 Verificador de Configuração - Google Gemini")
    print("=" * 60)
    
    # Verificar dependências
    if not check_dependencies():
        print("\n💡 Execute 'pip install -r requirements.txt' e tente novamente")
        return
    
    # Verificar arquivo .env
    if not check_env_file():
        return
    
    # Teste opcional de conexão
    test_connection = input("\n🧪 Deseja testar a conexão com a API? (s/n): ").lower()
    
    if test_connection == 's':
        if test_api_connection():
            print("\n🎉 Configuração completa e funcionando!")
            print("🚀 Você pode executar o dashboard: streamlit run app.py")
        else:
            print("\n⚠️  Configuração criada, mas teste falhou")
            print("   Verifique sua API key e tente novamente")
    else:
        print("\n✅ Configuração parece estar correta!")
        print("🚀 Você pode executar o dashboard: streamlit run app.py")

if __name__ == "__main__":
    main() 