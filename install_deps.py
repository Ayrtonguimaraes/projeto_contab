#!/usr/bin/env python3
"""
Script para instalar dependências automaticamente
"""

import subprocess
import sys
import os

def install_requirements():
    """
    Instala as dependências do requirements.txt
    """
    print("📦 Instalando dependências...")
    
    try:
        # Verificar se requirements.txt existe
        if not os.path.exists("requirements.txt"):
            print("❌ Arquivo requirements.txt não encontrado!")
            return False
        
        # Instalar dependências
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependências instaladas com sucesso!")
            return True
        else:
            print("❌ Erro ao instalar dependências:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    """
    Função principal
    """
    print("=" * 50)
    print("📦 Instalador de Dependências")
    print("=" * 50)
    
    if install_requirements():
        print("\n🎉 Instalação concluída!")
        print("💡 Agora você pode:")
        print("   1. Configurar a API: python check_gemini.py")
        print("   2. Executar o dashboard: streamlit run app.py")
    else:
        print("\n❌ Instalação falhou!")
        print("💡 Tente instalar manualmente:")
        print("   pip install -r requirements.txt")

if __name__ == "__main__":
    main() 