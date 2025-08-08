#!/usr/bin/env python3
"""
Script de inicialização do Dashboard de Análise Contábil
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """
    Verifica se as dependências estão instaladas
    """
    try:
        import streamlit
        import pandas
        import plotly
        import numpy
        print("✅ Todas as dependências estão instaladas!")
        return True
    except ImportError as e:
        print(f"❌ Dependência não encontrada: {e}")
        print("📦 Instalando dependências...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dependências instaladas com sucesso!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Erro ao instalar dependências. Execute manualmente:")
            print("   pip install -r requirements.txt")
            return False

def run_tests():
    """
    Executa os testes do aplicativo
    """
    print("🧪 Executando testes...")
    try:
        result = subprocess.run([sys.executable, "test_app.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Testes passaram com sucesso!")
            return True
        else:
            print("❌ Testes falharam:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Erro ao executar testes: {e}")
        return False

def start_dashboard():
    """
    Inicia o dashboard Streamlit
    """
    print("🚀 Iniciando Dashboard de Análise Contábil...")
    print("📊 O dashboard será aberto no seu navegador automaticamente.")
    print("🌐 URL: http://localhost:8501")
    print("⏹️  Para parar o servidor, pressione Ctrl+C")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Dashboard encerrado pelo usuário.")
    except Exception as e:
        print(f"❌ Erro ao iniciar dashboard: {e}")

def main():
    """
    Função principal
    """
    print("=" * 60)
    print("📊 Dashboard de Análise Contábil Interativo")
    print("=" * 60)
    
    # Verificar se estamos no diretório correto
    if not Path("app.py").exists():
        print("❌ Arquivo app.py não encontrado!")
        print("   Certifique-se de estar no diretório correto do projeto.")
        return
    
    # Verificar dependências
    if not check_dependencies():
        return
    
    # Executar testes
    if not run_tests():
        print("⚠️  Testes falharam, mas continuando...")
    
    # Iniciar dashboard
    start_dashboard()

if __name__ == "__main__":
    main() 