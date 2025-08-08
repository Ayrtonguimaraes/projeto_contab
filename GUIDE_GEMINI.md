# 🤖 Guia de Configuração - Google Gemini AI

Este guia explica como configurar a API do Google Gemini para usar a análise inteligente no dashboard contábil.

## 📋 Pré-requisitos

1. **Conta Google**: Você precisa de uma conta Google válida
2. **Acesso à API**: A API do Google Gemini é gratuita com limites generosos
3. **Python**: Versão 3.8 ou superior

## 🔑 Como Obter a API Key

### Passo 1: Acessar o Google AI Studio
1. Vá para: https://makersuite.google.com/app/apikey
2. Faça login com sua conta Google

### Passo 2: Criar API Key
1. Clique em **"Create API Key"**
2. Escolha **"Create API Key in new project"** ou use um projeto existente
3. Copie a chave gerada (algo como: `AIzaSyC...`)

### Passo 3: Configurar no Projeto
Execute o script de configuração:
```bash
python setup_gemini.py
```

Ou crie manualmente o arquivo `.env`:
```env
GOOGLE_GEMINI_API_KEY=sua_chave_aqui
GEMINI_MODEL=gemini-1.5-flash
MAX_TOKENS=4096
TEMPERATURE=0.7
```

## 🚀 Configuração (Recomendado)

### Método 1: Configuração Manual (Mais Seguro)
1. Crie um arquivo `.env` na raiz do projeto
2. Adicione sua API key:
   ```env
   GOOGLE_GEMINI_API_KEY=sua_chave_aqui
   ```

### Método 2: Usar Arquivo de Exemplo
```bash
cp config.env.example .env
# Edite o arquivo .env e substitua 'your_api_key_here' pela sua chave
```

### Método 3: Verificar Configuração
```bash
python check_gemini.py
```
- Verifica se a API key está configurada
- Testa se as dependências estão instaladas
- Oferece teste opcional de conexão

## 🔧 Configurações Avançadas

### Modelos Disponíveis
- `gemini-1.5-flash` (Recomendado - Rápido e eficiente)
- `gemini-1.5-pro` (Mais poderoso, mas mais lento)
- `gemini-pro` (Versão anterior)

### Parâmetros de Configuração
```env
# Modelo a ser usado
GEMINI_MODEL=gemini-1.5-flash

# Número máximo de tokens na resposta
MAX_TOKENS=4096

# Criatividade das respostas (0.0 = conservador, 1.0 = criativo)
TEMPERATURE=0.7
```

## 🧪 Testando a Configuração

### Teste Rápido
```bash
python setup_gemini.py
```
O script testará automaticamente a conexão.

### Teste Manual
```python
from ai_analyzer import AIAnalyzer

analyzer = AIAnalyzer()
if analyzer.is_available():
    print("✅ API configurada corretamente!")
else:
    print("❌ Problema na configuração")
```

## 🛠️ Solução de Problemas

### Erro: "API Key não configurada"
**Solução**: Verifique se o arquivo `.env` existe e contém a API key correta.

### Erro: "Invalid API Key"
**Solução**: 
1. Verifique se a API key está correta
2. Certifique-se de que copiou a chave completa
3. Tente criar uma nova API key

### Erro: "Quota exceeded"
**Solução**: 
- A API gratuita tem limites generosos
- Aguarde alguns minutos e tente novamente
- Considere fazer upgrade para plano pago se necessário

### Erro: "Model not found"
**Solução**: 
- Verifique se o modelo especificado existe
- Use `gemini-1.5-flash` como padrão

## 📊 Limites da API Gratuita

### Limites Diários
- **Requests**: 15 por minuto
- **Tokens**: 1M por minuto
- **Custo**: Gratuito

### Limites por Request
- **Input tokens**: 1M
- **Output tokens**: 1M
- **Tempo de resposta**: ~30 segundos

## 🔒 Segurança

### Proteção da API Key
- ✅ O arquivo `.env` está no `.gitignore`
- ✅ A chave não é exposta no código
- ✅ Use variáveis de ambiente para produção

### Boas Práticas
1. **Nunca** compartilhe sua API key
2. **Nunca** commite o arquivo `.env` no Git
3. Use chaves diferentes para desenvolvimento e produção
4. Monitore o uso da API regularmente

## 🎯 Exemplos de Uso

### Perguntas que você pode fazer:
- "Qual categoria de despesa tem o maior impacto?"
- "Como as receitas evoluíram nos últimos 6 meses?"
- "Quais são as principais tendências nos dados?"
- "Compare o desempenho entre diferentes categorias"
- "Identifique possíveis oportunidades de economia"

### Insights Automáticos
A IA irá gerar automaticamente:
- Resumo executivo
- Análise de performance
- Principais insights
- Recomendações estratégicas
- Alertas e pontos de atenção

## 📞 Suporte

Se você encontrar problemas:
1. Verifique se a API key está correta
2. Teste a conexão com `python setup_gemini.py`
3. Consulte a documentação oficial: https://ai.google.dev/
4. Verifique os limites da API gratuita

---

**🎉 Agora você está pronto para usar a análise inteligente no dashboard!** 