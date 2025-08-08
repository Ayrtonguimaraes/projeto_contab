# 📊 Dashboard de Análise Contábil Profissional com IA

## 🚀 **VISÃO GERAL**

Dashboard web interativo desenvolvido em Streamlit para **análise contábil e financeira corporativa** com inteligência artificial integrada. Transformou-se de um sistema básico de receitas/despesas em uma **plataforma profissional** adequada para analistas contábeis e executivos.

### **🎯 FUNCIONALIDADES PRINCIPAIS:**

#### **🤖 IA como Protagonista**
- **Chat interativo** com Google Gemini para análise inteligente
- **Seletor de gráficos** com preview visual automático
- **Histórico de conversas** organizadas por contexto
- **Sugestões inteligentes** de perguntas relevantes

#### **📈 Análise Financeira Corporativa**
- **37 indicadores financeiros** profissionais automatizados
- **8 páginas especializadas** de análise (Rentabilidade, Liquidez, DuPont, etc.)
- **Gráficos profissionais** com Plotly (radar, heatmap, subplots)
- **Dados reais brasileiros** com suporte a formato BR (1.234.567,89)

#### **🏗️ Arquitetura Modular**
- **Navegação por páginas** intuitiva
- **Código modular** escalável (config/, utils/, pages/)
- **Separação clara** de responsabilidades
- **Fácil manutenção** e extensibilidade

---

## 🛠️ **TECNOLOGIAS UTILIZADAS**

### **Frontend & UI:**
- **Streamlit 1.28.1** - Interface web responsiva
- **Plotly Express** - Gráficos interativos profissionais
- **CSS customizado** - Estilos profissionais

### **Backend & Análise:**
- **Pandas** - Manipulação de dados financeiros
- **NumPy** - Cálculos matemáticos avançados
- **Python 3.8+** - Linguagem principal

### **Inteligência Artificial:**
- **Google Gemini AI** - Análise inteligente especializada
- **Processamento de linguagem natural** - Chat contextual
- **Insights automáticos** - Análises personalizadas

---

## 📦 **INSTALAÇÃO E CONFIGURAÇÃO**

### **1️⃣ Pré-requisitos:**
```bash
# Python 3.8 ou superior
python --version

# pip atualizado
pip install --upgrade pip
```

### **2️⃣ Instalação:**

#### **Método Automático (Recomendado):**
```bash
# Clone o projeto
git clone <url-do-repositorio>
cd projeto_contab

# Instale dependências automaticamente
python install_deps.py
```

#### **Método Manual:**
```bash
# Instale dependências
pip install -r requirements.txt

# Instale dependências específicas se necessário
pip install streamlit pandas plotly google-generativeai python-dotenv
```

### **3️⃣ Configuração da IA (Opcional mas Recomendado):**

#### **Obter API Key:**
1. Acesse: https://makersuite.google.com/app/apikey
2. Crie sua conta Google (gratuita)
3. Gere uma nova API key

#### **Configurar Projeto:**
```bash
# Crie arquivo .env na raiz do projeto
echo "GOOGLE_GEMINI_API_KEY=sua_chave_aqui" > .env

# Ou copie do exemplo
cp config.env.example .env
# Edite o .env e substitua a chave
```

### **4️⃣ Executar o Dashboard:**
```bash
# Iniciar aplicação
streamlit run app.py

# Ou usar o script auxiliar
python run_dashboard.py
```

### **5️⃣ Testar Configuração:**
```bash
# Testar API Gemini (opcional)
python test_api_gemini.py

# Testar aplicação
python test_app.py
```

---

## 🎯 **COMO USAR**

### **📊 1. Dashboard Principal**
- **KPIs automáticos** na sidebar
- **Filtros dinâmicos** por período, categoria, tipo
- **5 tipos de gráficos** profissionais
- **Tabela detalhada** de transações

### **🤖 2. Chat com IA (Funcionalidade Central)**
1. **Selecione um gráfico** no dropdown
2. **Confirme visualmente** com preview automático
3. **Digite sua pergunta** ou use sugestões
4. **Receba análise especializada** da IA
5. **Explore histórico** de conversas anteriores

### **📈 3. Páginas Especializadas**
- **💰 Análise de Rentabilidade** - ROE, ROA, margens
- **🏦 Análise de Liquidez** - Liquidez geral, corrente, seca
- **📊 Dashboard Executivo** - Visão geral consolidada
- **🔍 Análise DuPont** - Decomposição da rentabilidade
- **⏱️ Ciclo Financeiro** - Prazos médios operacionais
- **🏗️ Estrutura de Capital** - Endividamento e composição

---

## 📊 **ESTRUTURA DOS DADOS**

### **📁 Dados Suportados:**
- **CSV brasileiro** - Formato 1.234.567,89
- **CSV internacional** - Formato 1234567.89
- **Dados fictícios** - Geração automática para testes
- **Dados reais** - Upload de planilhas corporativas

### **📋 Colunas Esperadas:**
```
Data, Descrição, Categoria, Tipo, Valor
2025-01-01, Venda produtos, Vendas, Receita, 15000.00
```

### **🏢 Categorias Corporativas:**
- **Receitas:** Vendas, Serviços, Consultoria, Investimentos
- **Despesas:** Salários, Marketing, Infraestrutura, Impostos
- **Análise:** 37 indicadores financeiros automatizados

---

## 🏗️ **ARQUITETURA DO PROJETO**

### **📁 Estrutura Modular:**
```
projeto_contab/
├── 🎯 app.py                    # Aplicação principal
├── 🤖 ai_analyzer.py            # Análise com IA
├── 📊 financial_analyzer.py     # Indicadores financeiros
├── 📈 chart_manager.py          # Gerenciador de gráficos
├── ⚙️ config/
│   ├── __init__.py
│   └── settings.py             # Configurações centralizadas
├── 🛠️ utils/
│   ├── __init__.py
│   └── data_loader.py          # Carregamento de dados
├── 📄 pages/
│   ├── __init__.py
│   ├── base_page.py           # Classe base para páginas
│   ├── dashboard_executivo.py # Dashboard principal
│   ├── analise_rentabilidade.py # Análise de rentabilidade
│   ├── chat_ia.py            # Interface de chat
│   └── page_manager.py       # Gerenciador de páginas
├── 📋 requirements.txt        # Dependências
├── 🔧 install_deps.py         # Instalador automático
├── 🧪 test_api_gemini.py      # Teste da API
└── 📖 README.md              # Esta documentação
```

### **🔧 Principais Módulos:**

#### **FinancialAnalyzer (`financial_analyzer.py`)**
- **37 indicadores** financeiros profissionais
- **Análise de rentabilidade** (ROE, ROA, margens)
- **Indicadores de liquidez** (geral, corrente, seca)
- **Estrutura de capital** (endividamento, composição)
- **Gráficos especializados** (radar, heatmap, subplots)

#### **AIAnalyzer (`ai_analyzer.py`)**
- **Chat inteligente** com contexto financeiro
- **Análise de gráficos** específicos
- **Prompts especializados** por tipo de análise
- **Serialização robusta** de dados complexos

#### **ChartManager (`chart_manager.py`)**
- **5 tipos de gráficos** profissionais
- **Miniaturas automáticas** para preview
- **Dados contextuais** para IA
- **Metadados organizados** por gráfico

---

## 🔧 **PERSONALIZAÇÃO E EXTENSÃO**

### **➕ Adicionar Novas Páginas:**
```python
# 1. Criar nova página em pages/
class NovaPagina(BasePage):
    def render(self):
        st.title("Nova Funcionalidade")
        # Implementar funcionalidade

# 2. Registrar no PageManager
PageManager.register_page("nova", NovaPagina())
```

### **📊 Adicionar Novos Gráficos:**
```python
# Em chart_manager.py
def create_novo_grafico(df_filtrado):
    # Implementar novo gráfico
    return fig, dados_para_ia
```

### **🤖 Personalizar IA:**
```python
# Em ai_analyzer.py
def custom_analysis_prompt(dados):
    return """
    Prompt personalizado para análise específica
    """
```

---

## 🐛 **SOLUÇÃO DE PROBLEMAS**

### **🔧 Problemas Comuns:**

#### **Erro de Dependências:**
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

#### **Porta Ocupada:**
```bash
streamlit run app.py --server.port 8502
```

#### **Erro de API Gemini:**
```bash
# Verificar configuração
python test_api_gemini.py

# Reconfigurar .env
echo "GOOGLE_GEMINI_API_KEY=nova_chave" > .env
```

#### **Erro de Dados Brasileiros:**
- **Formato suportado:** 1.234.567,89
- **Conversão automática:** Implementada
- **Fallback:** Dados fictícios se falhar

#### **Performance Lenta:**
- **Cache Streamlit:** Implementado automaticamente
- **Filtros de dados:** Use para reduzir volume
- **Gráficos otimizados:** Plotly com sampling

---

## 🎯 **FUNCIONALIDADES AVANÇADAS**

### **🤖 Chat com IA Especializada:**
- **Perguntas sugeridas:** "Qual o indicador mais crítico?"
- **Análise contextual:** IA entende qual gráfico está analisando
- **Insights acionáveis:** Recomendações práticas
- **Histórico preservado:** Conversas anteriores organizadas

### **📊 Análise Financeira Profissional:**
- **Indicadores de Rentabilidade:** ROE, ROA, margem líquida
- **Indicadores de Liquidez:** LG, LC, LS, liquidez imediata
- **Estrutura de Capital:** Endividamento, composição
- **Análise DuPont:** Decomposição matemática da rentabilidade
- **Ciclo Financeiro:** PMRE, PMRV, PMPC automatizados

### **🎨 Visualizações Avançadas:**
- **Gráficos Radar:** Visão multidimensional
- **Heatmaps:** Comparações normalizadas
- **Subplots:** Múltiplas análises integradas
- **Interatividade:** Zoom, filtros, hover

---

## 🚀 **ROADMAP E EVOLUÇÃO**

### **✅ Implementado:**
- ✅ IA como funcionalidade central
- ✅ Arquitetura modular completa
- ✅ 37 indicadores financeiros
- ✅ 8 páginas especializadas
- ✅ Suporte a dados brasileiros
- ✅ Interface de chat avançada

### **🔮 Próximas Funcionalidades:**
- 🔄 **Integração com APIs** bancárias
- 📱 **Versão mobile-first** responsiva
- 🎨 **Temas personalizáveis** e modo escuro
- 🤖 **IA multi-modelo** (GPT + Gemini)
- 📊 **Novos tipos** de visualização
- 🔐 **Autenticação** e multi-usuário
- 📈 **Análises preditivas** com ML
- 🌐 **Internacionalização** (EN/ES)

---

## 📄 **LICENÇA E CONTRIBUIÇÃO**

### **📝 Licença:**
Este projeto está sob a **licença MIT**. Livre para uso comercial e pessoal.

### **🤝 Como Contribuir:**
1. **Fork** o repositório
2. **Crie branch** para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. **Implemente** suas mudanças
4. **Teste** completamente (`python test_app.py`)
5. **Commit** com mensagens claras (`git commit -m 'Adiciona nova funcionalidade'`)
6. **Push** para branch (`git push origin feature/nova-funcionalidade`)
7. **Abra Pull Request** com descrição detalhada

### **📞 Suporte:**
- 🐛 **Issues:** Para bugs e problemas
- 💡 **Discussions:** Para ideias e sugestões
- 📧 **Contato:** [seu-email@exemplo.com]

---

## 🏆 **MARCOS E VERSÕES**

### **📊 v1.0 - Dashboard Básico**
- Dashboard simples de receitas/despesas
- Gráficos básicos com Plotly
- Filtros dinâmicos

### **🤖 v2.0 - IA como Protagonista**
- Chat inteligente central
- Análise de gráficos específicos
- Interface de conversação

### **🏢 v3.0 - Análise Corporativa (Atual)**
- 37 indicadores financeiros profissionais
- 8 páginas especializadas
- Arquitetura modular completa
- Suporte a dados brasileiros reais

---

**🎯 Desenvolvido com ❤️ para transformar análise financeira em insights acionáveis através da inteligência artificial!**

---

*Última atualização: Janeiro 2025 - v3.0 Professional*
