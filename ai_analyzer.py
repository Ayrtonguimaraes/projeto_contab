import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os
from dotenv import load_dotenv
import numpy as np  # Adicionado para uso em _convert_to_serializable

# Carregar variáveis de ambiente
load_dotenv()

class AIAnalyzer:
    """
    Classe para análise de dados usando Google Gemini AI
    """
    
    def __init__(self):
        """
        Inicializa o analisador de IA
        """
        self.api_key = os.getenv('GOOGLE_GEMINI_API_KEY')
        self.model_name = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
        self.max_tokens = int(os.getenv('MAX_TOKENS', 4096))
        self.temperature = float(os.getenv('TEMPERATURE', 0.7))
        self.detail_level = os.getenv('LLM_DETAIL_LEVEL', 'balanced').lower()
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=self.max_tokens,
                    temperature=self.temperature
                )
            )
        else:
            self.model = None
            st.warning("⚠️ API Key do Google Gemini não configurada. Configure a variável GOOGLE_GEMINI_API_KEY no arquivo .env")
    
    def is_available(self):
        """
        Verifica se a IA está disponível
        """
        return self.model is not None
    
    def _convert_to_serializable(self, obj):
        """
        Converte objetos para formatos JSON-serializáveis
        """
        import pandas as pd
        import numpy as np
        from datetime import datetime, date
        
        # Para DataFrames, converter diretamente sem verificar isna
        if isinstance(obj, pd.DataFrame):
            return self._convert_to_serializable(obj.to_dict('records'))
            
        # Para Series, converter diretamente sem verificar isna
        if isinstance(obj, pd.Series):
            return self._convert_to_serializable(obj.to_dict())
        
        # Verifica se é NaN ou None para outros tipos
        if obj is None:
            return None
            
        # Para tipos escalares, verificar se é NaN
        try:
            if pd.isna(obj):
                return None
        except (TypeError, ValueError):
            # Se pd.isna falhar, continuar com outros testes
            pass
            
        # Pandas Timestamp
        if isinstance(obj, pd.Timestamp):
            return obj.strftime('%d/%m/%Y')
            
        # Pandas Period (para dados mensais)
        if hasattr(obj, 'strftime') and hasattr(obj, 'freq'):
            return obj.strftime('%m/%Y')
            
        # Numpy datetime64
        if isinstance(obj, np.datetime64):
            return pd.Timestamp(obj).strftime('%d/%m/%Y')
            
        # Datetime python nativo
        if isinstance(obj, (datetime, date)):
            return obj.strftime('%d/%m/%Y')
            
        # Numpy types
        if isinstance(obj, (np.integer, np.floating)):
            return float(obj)
            
        # Dictionary
        if isinstance(obj, dict):
            return {k: self._convert_to_serializable(v) for k, v in obj.items()}
            
        # List or tuple
        elif isinstance(obj, (list, tuple)):
            return [self._convert_to_serializable(item) for item in obj]
            
        # Tipos básicos
        elif isinstance(obj, (int, float, str, bool)):
            return obj
            
        # Outros objetos com método to_dict
        elif hasattr(obj, 'to_dict'):
            return self._convert_to_serializable(obj.to_dict())
            
        # Outros objetos com método tolist
        elif hasattr(obj, 'tolist'):
            return self._convert_to_serializable(obj.tolist())
            
        # Converter para string como último recurso
        else:
            return str(obj)
    
    def _prepare_temporal_analysis(self, df_filtrado):
        """
        Prepara análise temporal detalhada dos dados
        """
        try:
            if df_filtrado.empty:
                return {"erro": "Não há dados para análise temporal"}
            
            # Criar cópia para manipulação
            df_temp = df_filtrado.copy()
            df_temp['Ano'] = df_temp['Data'].dt.year
            df_temp['Mes'] = df_temp['Data'].dt.month
            df_temp['Mes_Nome'] = df_temp['Data'].dt.strftime('%B')
            df_temp['Mes_Ano'] = df_temp['Data'].dt.strftime('%m/%Y')
            df_temp['Trimestre'] = df_temp['Data'].dt.quarter
            df_temp['Dia_Semana'] = df_temp['Data'].dt.strftime('%A')
            
            # Análise por mês/ano
            receitas_por_mes = df_temp[df_temp['Tipo'] == 'Receita'].groupby('Mes_Ano')['Valor'].sum().to_dict()
            despesas_por_mes = df_temp[df_temp['Tipo'] == 'Despesa'].groupby('Mes_Ano')['Valor'].sum().to_dict()
            
            # Conversão segura para float
            receitas_por_mes = {k: float(v) for k, v in receitas_por_mes.items()}
            despesas_por_mes = {k: float(v) for k, v in despesas_por_mes.items()}
            
            # Análise por trimestre
            receitas_por_trimestre = df_temp[df_temp['Tipo'] == 'Receita'].groupby(['Ano', 'Trimestre'])['Valor'].sum()
            despesas_por_trimestre = df_temp[df_temp['Tipo'] == 'Despesa'].groupby(['Ano', 'Trimestre'])['Valor'].sum()
            
            # Converter para dicionário com chaves strings
            receitas_trimestre_dict = {}
            for (ano, trim), valor in receitas_por_trimestre.items():
                receitas_trimestre_dict[f"{ano}_Q{trim}"] = float(valor)
                
            despesas_trimestre_dict = {}
            for (ano, trim), valor in despesas_por_trimestre.items():
                despesas_trimestre_dict[f"{ano}_Q{trim}"] = float(valor)
            
            return {
                "receitas_por_mes": receitas_por_mes,
                "despesas_por_mes": despesas_por_mes,
                "receitas_por_trimestre": receitas_trimestre_dict,
                "despesas_por_trimestre": despesas_trimestre_dict,
                "periodo_analise": {
                    "primeiro_mes": min(receitas_por_mes.keys()) if receitas_por_mes else "N/A",
                    "ultimo_mes": max(receitas_por_mes.keys()) if receitas_por_mes else "N/A",
                    "total_meses": len(set(list(receitas_por_mes.keys()) + list(despesas_por_mes.keys())))
                }
            }
            
        except Exception as e:
            return {"erro": f"Erro na análise temporal: {str(e)}"}
    
    def _prepare_trend_analysis(self, df_filtrado):
        """
        Prepara análise de tendências dos dados
        """
        try:
            if df_filtrado.empty:
                return {"erro": "Não há dados para análise de tendências"}
            
            # Criar cópia para manipulação
            df_temp = df_filtrado.copy()
            df_temp['Mes_Ano'] = df_temp['Data'].dt.strftime('%m/%Y')
            
            # Calcular crescimento mês a mês
            receitas_mensais = df_temp[df_temp['Tipo'] == 'Receita'].groupby('Mes_Ano')['Valor'].sum().sort_index()
            despesas_mensais = df_temp[df_temp['Tipo'] == 'Despesa'].groupby('Mes_Ano')['Valor'].sum().sort_index()
            
            # Verificar se há dados suficientes
            if len(receitas_mensais) < 2:
                return {
                    "erro": "Dados insuficientes para análise de tendências",
                    "receita_media_mensal": float(receitas_mensais.mean()) if not receitas_mensais.empty else 0,
                    "despesa_media_mensal": float(despesas_mensais.mean()) if not despesas_mensais.empty else 0
                }
            
            # Calcular variações percentuais
            receitas_crescimento = {}
            despesas_crescimento = {}
            
            receitas_list = receitas_mensais.tolist()
            despesas_list = despesas_mensais.tolist()
            meses = receitas_mensais.index.tolist()
            
            # Calcular crescimento para receitas
            for i in range(1, len(receitas_list)):
                if receitas_list[i-1] != 0:
                    var_receita = ((receitas_list[i] - receitas_list[i-1]) / receitas_list[i-1]) * 100
                    receitas_crescimento[str(meses[i])] = round(float(var_receita), 2)
            
            # Calcular crescimento para despesas
            for i in range(1, len(despesas_list)):
                if len(despesas_list) > i-1 and despesas_list[i-1] != 0:
                    var_despesa = ((despesas_list[i] - despesas_list[i-1]) / despesas_list[i-1]) * 100
                    despesas_crescimento[str(meses[i])] = round(float(var_despesa), 2)
            
            # Identificar tendências (apenas se houver pelo menos 3 pontos)
            receita_tendencia = "estável"
            if len(receitas_list) >= 3:
                ultimos_3 = receitas_list[-3:]
                if all(ultimos_3[i] > ultimos_3[i-1] for i in range(1, len(ultimos_3))):
                    receita_tendencia = "crescente"
                elif all(ultimos_3[i] < ultimos_3[i-1] for i in range(1, len(ultimos_3))):
                    receita_tendencia = "decrescente"
            
            despesa_tendencia = "estável"
            if len(despesas_list) >= 3:
                ultimos_3 = despesas_list[-3:]
                if all(ultimos_3[i] > ultimos_3[i-1] for i in range(1, len(ultimos_3))):
                    despesa_tendencia = "crescente"
                elif all(ultimos_3[i] < ultimos_3[i-1] for i in range(1, len(ultimos_3))):
                    despesa_tendencia = "decrescente"
            
            return {
                "crescimento_receitas": receitas_crescimento,
                "crescimento_despesas": despesas_crescimento,
                "tendencia_receita": receita_tendencia,
                "tendencia_despesa": despesa_tendencia,
                "receita_media_mensal": float(sum(receitas_list) / len(receitas_list)) if receitas_list else 0,
                "despesa_media_mensal": float(sum(despesas_list) / len(despesas_list)) if despesas_list else 0,
                "meses_analisados": len(receitas_list),
                "primeiro_mes": str(meses[0]) if meses else "N/A",
                "ultimo_mes": str(meses[-1]) if meses else "N/A"
            }
            
        except Exception as e:
            return {"erro": f"Erro na análise de tendências: {str(e)}"}
    
    def _prepare_monthly_ranking(self, df_filtrado):
        """
        Prepara ranking detalhado por mês
        """
        try:
            if df_filtrado.empty:
                return {"erro": "Não há dados para ranking mensal"}
            
            # Criar cópia para manipulação
            df_temp = df_filtrado.copy()
            df_temp['Mes_Ano'] = df_temp['Data'].dt.strftime('%m/%Y')
            df_temp['Mes_Nome_Ano'] = df_temp['Data'].dt.strftime('%B de %Y')
            
            # Agrupar por mês
            receitas_por_mes = df_temp[df_temp['Tipo'] == 'Receita'].groupby(['Mes_Ano', 'Mes_Nome_Ano'])['Valor'].sum()
            despesas_por_mes = df_temp[df_temp['Tipo'] == 'Despesa'].groupby(['Mes_Ano', 'Mes_Nome_Ano'])['Valor'].sum()
            saldo_por_mes = receitas_por_mes.subtract(despesas_por_mes, fill_value=0)
            
            # Ranking de receitas
            ranking_receitas = []
            for (mes_ano, mes_nome), valor in receitas_por_mes.sort_values(ascending=False).items():
                ranking_receitas.append({
                    "mes_ano": mes_ano,
                    "mes_nome": mes_nome,
                    "valor": float(valor),
                    "posicao": len(ranking_receitas) + 1
                })
            
            # Ranking de despesas
            ranking_despesas = []
            for (mes_ano, mes_nome), valor in despesas_por_mes.sort_values(ascending=False).items():
                ranking_despesas.append({
                    "mes_ano": mes_ano,
                    "mes_nome": mes_nome,
                    "valor": float(valor),
                    "posicao": len(ranking_despesas) + 1
                })
            
            # Ranking de saldo
            ranking_saldo = []
            for (mes_ano, mes_nome), valor in saldo_por_mes.sort_values(ascending=False).items():
                ranking_saldo.append({
                    "mes_ano": mes_ano,
                    "mes_nome": mes_nome,
                    "saldo": float(valor),
                    "posicao": len(ranking_saldo) + 1
                })
            
            # Melhor e pior mês
            melhor_receita = ranking_receitas[0] if ranking_receitas else None
            pior_receita = ranking_receitas[-1] if ranking_receitas else None
            melhor_saldo = ranking_saldo[0] if ranking_saldo else None
            pior_saldo = ranking_saldo[-1] if ranking_saldo else None
            
            return {
                "ranking_receitas": ranking_receitas[:5],  # Top 5
                "ranking_despesas": ranking_despesas[:5],  # Top 5
                "ranking_saldo": ranking_saldo,
                "melhor_mes_receita": melhor_receita,
                "pior_mes_receita": pior_receita,
                "melhor_mes_saldo": melhor_saldo,
                "pior_mes_saldo": pior_saldo
            }
            
        except Exception as e:
            return {"erro": f"Erro no ranking mensal: {str(e)}"}
    
    def _build_executive_alerts_and_narrative(self, df):
        """Gera alertas executivos e narrativa resumida a partir do DF financeiro (anos)."""
        try:
            if df is None or df.empty or 'Ano' not in df.columns or len(df['Ano'].unique()) < 2:
                return [], None
            df_sorted = df.sort_values('Ano')
            prev, cur = df_sorted.iloc[-2], df_sorted.iloc[-1]
            ano_prev, ano_cur = int(df_sorted['Ano'].iloc[-2]), int(df_sorted['Ano'].iloc[-1])
            alerts = []
            def pct_delta(a,b):
                try:
                    return (b-a)/a*100 if a not in (0,None) else None
                except: return None
            # Liquidez Corrente
            if 'Liquidez Corrente (LC) ' in df.columns:
                lc_cur = cur['Liquidez Corrente (LC) ']
                if lc_cur < 1.0:
                    alerts.append({"nivel":"critico","mensagem":f"Liquidez Corrente {lc_cur:.2f} abaixo de 1.0","ano":ano_cur})
                elif lc_cur < 1.2:
                    alerts.append({"nivel":"atencao","mensagem":f"Liquidez Corrente {lc_cur:.2f} em zona de atenção (<1.2)","ano":ano_cur})
            # Liquidez Imediata queda
            if 'Liquidez Imediata (LI)' in df.columns:
                li_delta = cur['Liquidez Imediata (LI)'] - prev['Liquidez Imediata (LI)']
                if li_delta < -0.1:
                    alerts.append({"nivel":"atencao","mensagem":f"Liquidez Imediata caiu {li_delta:.2f} vs {ano_prev}","ano":ano_cur})
            # Endividamento Geral
            if 'Endividamento Geral (EG)' in df.columns:
                eg_delta_pct = pct_delta(prev['Endividamento Geral (EG)'], cur['Endividamento Geral (EG)'])
                if eg_delta_pct is not None and eg_delta_pct > 10:
                    alerts.append({"nivel":"atencao","mensagem":f"Endividamento Geral +{eg_delta_pct:.1f}% vs {ano_prev}","ano":ano_cur})
            # Margem Líquida queda
            if 'Margem Líquida (ML)' in df.columns:
                ml_var_pp = (cur['Margem Líquida (ML)'] - prev['Margem Líquida (ML)'])*100
                if ml_var_pp < -2:
                    alerts.append({"nivel":"critico","mensagem":f"Margem Líquida caiu {ml_var_pp:.1f} pp vs {ano_prev}","ano":ano_cur})
            # ROE queda
            if 'Rentabilidade do Patrimônio Líquido (ROE) ' in df.columns:
                roe_var_pp = (cur['Rentabilidade do Patrimônio Líquido (ROE) '] - prev['Rentabilidade do Patrimônio Líquido (ROE) '])*100
                if roe_var_pp < -3:
                    alerts.append({"nivel":"critico","mensagem":f"ROE recuou {roe_var_pp:.1f} pp vs {ano_prev}","ano":ano_cur})
            # Narrativa
            parts = []
            def safe_pct(col):
                if col in df.columns:
                    try:
                        return (cur[col]-prev[col])/abs(prev[col])*100 if prev[col] not in (0,None) else None
                    except: return None
                return None
            roe_pct = safe_pct('Rentabilidade do Patrimônio Líquido (ROE) ')
            ml_pct = safe_pct('Margem Líquida (ML)')
            eg_pct = safe_pct('Endividamento Geral (EG)')
            lc_cur = cur['Liquidez Corrente (LC) '] if 'Liquidez Corrente (LC) ' in df.columns else None
            if roe_pct is not None:
                direction = 'recuo' if roe_pct < 0 else 'alta'
                parts.append(f"ROE {direction} {abs(roe_pct):.1f}%")
            if ml_pct is not None:
                parts.append(f"Margem {ml_pct:+.1f}%")
            if eg_pct is not None:
                if eg_pct > 0:
                    parts.append(f"Endividamento +{eg_pct:.1f}%")
                elif eg_pct < 0:
                    parts.append(f"Endividamento -{abs(eg_pct):.1f}%")
            if lc_cur is not None:
                parts.append(f"LC {lc_cur:.2f}")
            criticos = [a for a in alerts if a['nivel']=='critico']
            if criticos:
                parts.append(f"{len(criticos)} alerta(s) crítico(s)")
            narrativa = "; ".join(parts)+"." if parts else None
            return alerts, narrativa
        except Exception:
            return [], None
    def prepare_data_context(self, df, df_filtrado, kpis):
        """
        Prepara o contexto dos dados para a IA com análise temporal detalhada
        """
        try:
            # Preparar dados básicos
            dados_gerais = {
                "total_registros": int(len(df)),
                "registros_filtrados": int(len(df_filtrado)),
                "periodo_inicio": self._convert_to_serializable(df['Data'].min()),
                "periodo_fim": self._convert_to_serializable(df['Data'].max()),
                "categorias_receitas": df[df['Tipo'] == 'Receita']['Categoria'].unique().tolist(),
                "categorias_despesas": df[df['Tipo'] == 'Despesa']['Categoria'].unique().tolist()
            }
            
            # Preparar KPIs - garantir que são float
            kpis_atuais = {
                "receita_total": float(kpis.get('receita_total', 0)),
                "despesa_total": float(kpis.get('despesa_total', 0)),
                "saldo": float(kpis.get('saldo', 0))
            }
            
            # ===== NOVA SEÇÃO: ANÁLISE TEMPORAL DETALHADA =====
            analise_temporal = self._prepare_temporal_analysis(df_filtrado)
            
            # ===== NOVA SEÇÃO: ANÁLISE DE TENDÊNCIAS =====
            analise_tendencias = self._prepare_trend_analysis(df_filtrado)
            
            # ===== NOVA SEÇÃO: RANKING DE MESES =====
            ranking_mensal = self._prepare_monthly_ranking(df_filtrado)
            
            # Preparar dados filtrados com conversão segura
            resumo_estatistico = {}
            try:
                desc = df_filtrado.describe()
                # Converter apenas as colunas numéricas
                for col in desc.columns:
                    if col == 'Valor':  # Apenas a coluna de valor nos interessa
                        resumo_estatistico[col] = self._convert_to_serializable(desc[col].to_dict())
            except Exception as e:
                resumo_estatistico = {"erro": f"Não foi possível gerar estatísticas: {str(e)}"}
            
            # Top receitas com conversão segura
            top_receitas = []
            try:
                receitas_top = df_filtrado[df_filtrado['Tipo'] == 'Receita'].nlargest(5, 'Valor')
                for _, row in receitas_top.iterrows():
                    top_receitas.append({
                        'Data': self._convert_to_serializable(row['Data']),
                        'Descrição': str(row['Descrição']),
                        'Categoria': str(row['Categoria']),
                        'Valor': float(row['Valor']),
                        'Mes_Ano': self._convert_to_serializable(row['Data'].strftime('%m/%Y'))
                    })
            except Exception as e:
                top_receitas = [{"erro": f"Não foi possível obter top receitas: {str(e)}"}]
            
            # Top despesas com conversão segura
            top_despesas = []
            try:
                despesas_top = df_filtrado[df_filtrado['Tipo'] == 'Despesa'].nlargest(5, 'Valor')
                for _, row in despesas_top.iterrows():
                    top_despesas.append({
                        'Data': self._convert_to_serializable(row['Data']),
                        'Descrição': str(row['Descrição']),
                        'Categoria': str(row['Categoria']),
                        'Valor': float(row['Valor']),
                        'Mes_Ano': self._convert_to_serializable(row['Data'].strftime('%m/%Y'))
                    })
            except Exception as e:
                top_despesas = [{"erro": f"Não foi possível obter top despesas: {str(e)}"}]
            
            # Distribuição por categorias com conversão segura
            distribuicao_categorias = {}
            try:
                dist = df_filtrado.groupby(['Tipo', 'Categoria'])['Valor'].sum()
                for (tipo, categoria), valor in dist.items():
                    key = f"{tipo}_{categoria}"
                    distribuicao_categorias[key] = float(valor)
            except Exception as e:
                distribuicao_categorias = {"erro": f"Não foi possível calcular distribuição: {str(e)}"}
            
            dados_filtrados = {
                "resumo_estatistico": resumo_estatistico,
                "top_receitas": top_receitas,
                "top_despesas": top_despesas,
                "distribuicao_categorias": distribuicao_categorias,
                "analise_temporal": analise_temporal,
                "analise_tendencias": analise_tendencias,
                "ranking_mensal": ranking_mensal
            }
            
            context = {
                "dados_gerais": dados_gerais,
                "kpis_atuais": kpis_atuais,
                "dados_filtrados": dados_filtrados
            }
            # Adicionar alertas e narrativa executiva se aplicável
            alerts, narrativa = self._build_executive_alerts_and_narrative(df_filtrado if 'Ano' in df_filtrado.columns else df)
            if alerts:
                context["executive_alerts"] = alerts
            if narrativa:
                context["executive_narrative"] = narrativa
            return context
            
        except Exception as e:
            # Retornar contexto mínimo em caso de erro
            return {
                "erro": f"Erro ao preparar contexto: {str(e)}",
                "kpis_atuais": {
                    "receita_total": float(kpis.get('receita_total', 0)),
                    "despesa_total": float(kpis.get('despesa_total', 0)),
                    "saldo": float(kpis.get('saldo', 0))
                }
            }
    
    def generate_insights(self, df, df_filtrado, kpis, user_question=None):
        """
        Gera insights usando a IA do Google Gemini
        """
        if not self.is_available():
            return "IA não disponível. Configure a API key do Google Gemini."
        
        try:
            # Preparar contexto dos dados
            context = self.prepare_data_context(df, df_filtrado, kpis)
            
            # Verificar se houve erro na preparação do contexto
            if "erro" in context:
                return f"Erro na preparação dos dados: {context.get('erro', 'Erro desconhecido')}"
            
            # Construir prompt
            if user_question:
                prompt = self._build_question_prompt(context, user_question)
            else:
                prompt = self._build_insights_prompt(context)
            
            # Gerar resposta
            response = self.model.generate_content(prompt)
            
            return response.text
            
        except Exception as e:
            return f"Erro ao gerar insights: {str(e)}"
    
    # ===================== PROMPT TEMPLATES REFACTORED =====================
    def _select_detail_config(self):
        mapping = {
            'curto': {'bullets_destaques': 3, 'bullets_riscos': 2, 'bullets_acoes': 2, 'max_sections': 5},
            'balanced': {'bullets_destaques': 5, 'bullets_riscos': 3, 'bullets_acoes': 3, 'max_sections': 6},
            'detalhado': {'bullets_destaques': 8, 'bullets_riscos': 5, 'bullets_acoes': 5, 'max_sections': 7}
        }
        return mapping.get(self.detail_level, mapping['balanced'])

    def _format_context_compact(self, context: dict):
        """Reduz o contexto antes de enviar ao LLM (remove listas muito grandes)."""
        import copy
        ctx = copy.deepcopy(context)
        # Limitar top listas
        def trim_list(lst, n=10):
            return lst[:n] if isinstance(lst, list) and len(lst) > n else lst
        # Exemplos de cortes
        if isinstance(ctx.get('dados_filtrados'), dict):
            dfilt = ctx['dados_filtrados']
            for k in ['top_receitas','top_despesas','ranking_mensal']:
                if k in dfilt:
                    dfilt[k] = trim_list(dfilt[k], 5)
        return ctx

    def _build_insights_prompt(self, context):
        cfg = self._select_detail_config()
        ctx_compact = self._format_context_compact(context)
        prompt = f"""
Você é um analista financeiro sênior. Gere análise EXECUTIVA com profundidade equilibrada.
LÍNGUA: Português brasileiro.
FORMATO: Markdown estruturado.
NÍVEL DE DETALHE: {self.detail_level}.

DADOS (JSON resumido):
{json.dumps(ctx_compact, indent=2, ensure_ascii=False)}

INSTRUÇÕES GERAIS:
1. Se existirem executive_alerts, iniciar explicando-os em ordem de criticidade.
2. Usar executive_narrative como base, mas expandir com números objetivos (não inventar).
3. Citar métricas com valores e variações (pp ou %), sempre indicar unidade (% / vezes / R$ se aplicável).
4. Não repetir exatamente o mesmo valor em seções diferentes sem nova interpretação.
5. Se algum dado essencial estiver ausente, declarar 'dado não disponível'.
6. Evitar floreios; foco em implicações.

ESTRUTURA (não adicionar seções extras):
## 📌 Resumo Executivo (3-4 frases)
## 🔔 Alertas Críticos (se houver)
## 📊 Destaques Quantitativos (até {cfg['bullets_destaques']} bullets)
## ⚠️ Riscos / Pressões (até {cfg['bullets_riscos']} bullets)
## 🚀 Oportunidades / Eficiências (2-3 bullets)
## 🎯 Ações Prioritárias (até {cfg['bullets_acoes']} bullets com verbo inicial)
## 🧪 Observações / Limitações (1-2 bullets se necessário)

REGRAS DE NUMERAIS:
- Percentuais: 1 casa (ex: 12,3%).
- Diferença percentual absoluta: usar 'pp' quando for diferença de margens/ROE.
- Valores monetários: se houver (R$), sem casas decimais, milhar com ponto.

RESPONDA APENAS COM A ANÁLISE.
"""
        return prompt

    def _build_question_prompt(self, context, question):
        cfg = self._select_detail_config()
        ctx_compact = self._format_context_compact(context)
        prompt = f"""
Você é um analista financeiro sênior. Responda a PERGUNTA específica de forma objetiva porém com substância.
LÍNGUA: Português brasileiro.
NÍVEL DE DETALHE: {self.detail_level}.

PERGUNTA:
{question}

DADOS (JSON resumido):
{json.dumps(ctx_compact, indent=2, ensure_ascii=False)}

INSTRUÇÕES:
1. Se a pergunta se relacionar a métricas presentes em executive_alerts, priorize riscos primeiro.
2. Limitar a resposta a 3-5 parágrafos curtos OU uma combinação de parágrafos + lista (máx {cfg['bullets_destaques']} bullets totais).
3. Sempre que citar variação, qualificar (ex: 'ROE caiu 3,2 pp vs ano anterior').
4. Se a pergunta pedir comparação temporal e só houver 2 anos, explicitar limitação.
5. Encerrar (última linha) com '➡️ Próximo passo:' e uma recomendação acionável.
6. Não inventar métricas inexistentes; se não encontrado, dizer explicitamente.

FORMATO:
- Parágrafo inicial direto respondendo.
- Lista (se pertinente) com evidências numéricas.
- Conclusão estratégica + próximo passo.

RESPONDA APENAS COM O CONTEÚDO SOLICITADO.
"""
        return prompt
    
    def _convert_alerts_to_text(self, alerts):
        """
        Converte a lista de alertas em texto formatado para exibição
        """
        if not alerts:
            return "Nenhum alerta crítico."
        
        alertas_texto = []
        for alerta in alerts:
            if alerta['nivel'] == 'critico':
                alertas_texto.append(f"⚠️ **Crítico:** {alerta['mensagem']} (Ano: {alerta['ano']})")
            elif alerta['nivel'] == 'atencao':
                alertas_texto.append(f"⚠️ **Atenção:** {alerta['mensagem']} (Ano: {alerta['ano']})")
        
        return "\n".join(alertas_texto)
    
    def _prepare_temporal_context(self, df):
        """
        Prepara contexto temporal para análise detalhada
        """
        try:
            if df is None or df.empty:
                return {}
            
            # Agrupar por ano e mês
            df_temp = df.copy()
            df_temp['Ano'] = df_temp['Data'].dt.year
            df_temp['Mes'] = df_temp['Data'].dt.month
            df_temp['Mes_Ano'] = df_temp['Data'].dt.strftime('%m/%Y')
            
            # Calcular totais por mês
            totais_mensais = df_temp.groupby('Mes_Ano')['Valor'].sum().reset_index()
            totais_mensais['Tipo'] = 'Total'
            
            # Calcular totais por ano
            totais_anuais = df_temp.groupby('Ano')['Valor'].sum().reset_index()
            totais_anuais['Mes_Ano'] = totais_anuais['Ano'].astype(str)
            totais_anuais['Tipo'] = 'Total'
            
            # Combinar totais mensais e anuais
            contexto_temporal = pd.concat([totais_mensais, totais_anuais], ignore_index=True, sort=False)
            
            return contexto_temporal
            
        except Exception as e:
            return {"erro": f"Erro ao preparar contexto temporal: {str(e)}"}
    
    def _prepare_categorical_context(self, df):
        """
        Prepara contexto categorial para análise detalhada
        """
        try:
            if df is None or df.empty:
                return {}
            
            # Agrupar por categoria e tipo
            df_temp = df.copy()
            df_temp['Tipo'] = df_temp['Tipo'].astype(str)
            
            contexto_categorial = df_temp.groupby(['Categoria', 'Tipo'])['Valor'].sum().reset_index()
            
            return contexto_categorial
            
        except Exception as e:
            return {"erro": f"Erro ao preparar contexto categorial: {str(e)}"}
    
    def _prepare_trend_context(self, df):
        """
        Prepara contexto para análise de tendências
        """
        try:
            if df is None or df.empty:
                return {}
            
            # Ordenar por data
            df_sorted = df.sort_values('Data')
            
            # Calcular variação percentual mensal
            df_sorted['Variação Percentual'] = df_sorted.groupby('Tipo')['Valor'].pct_change() * 100
            
            # Filtrar apenas meses com dados
            contexto_tendencia = df_sorted.dropna(subset=['Variação Percentual'])
            
            return contexto_tendencia
            
        except Exception as e:
            return {"erro": f"Erro ao preparar contexto de tendência: {str(e)}"}
    
    def _prepare_chart_context(self, df_filtrado, chart_type):
        """
        Prepara contexto específico para análise de gráficos
        """
        try:
            context = {}
            
            if chart_type == "evolucao_temporal":
                # Análise específica para gráfico de evolução
                df_temp = df_filtrado.copy()
                df_temp['Mes_Ano'] = df_temp['Data'].dt.strftime('%m/%Y')
                
                evolucao = df_temp.groupby(['Mes_Ano', 'Tipo'])['Valor'].sum().unstack(fill_value=0)
                
                # Preparar dados seguros
                receita_col = 'Receita' if 'Receita' in evolucao.columns else None
                despesa_col = 'Despesa' if 'Despesa' in evolucao.columns else None
                
                context = {
                    "tipo_analise": "evolução temporal",
                    "periodos_analisados": len(df_temp['Mes_Ano'].unique()),
                    "primeiro_periodo": str(df_temp['Mes_Ano'].min()),
                    "ultimo_periodo": str(df_temp['Mes_Ano'].max()),
                    "receita_maxima": float(evolucao[receita_col].max()) if receita_col and not evolucao[receita_col].empty else 0,
                    "despesa_maxima": float(evolucao[despesa_col].max()) if despesa_col and not evolucao[despesa_col].empty else 0,
                    "mes_maior_receita": str(evolucao[receita_col].idxmax()) if receita_col and not evolucao[receita_col].empty else "N/A",
                    "mes_maior_despesa": str(evolucao[despesa_col].idxmax()) if despesa_col and not evolucao[despesa_col].empty else "N/A"
                }
                
            elif chart_type == "despesas_categoria":
                # Análise específica para gráfico de despesas por categoria
                despesas = df_filtrado[df_filtrado['Tipo'] == 'Despesa']
                if not despesas.empty:
                    por_categoria = despesas.groupby('Categoria')['Valor'].sum().sort_values(ascending=False)
                    if not por_categoria.empty:
                        total_despesas = float(por_categoria.sum())
                        top_3_sum = float(por_categoria.head(3).sum())
                        
                        context = {
                            "tipo_analise": "despesas por categoria",
                            "total_categorias": len(por_categoria),
                            "categoria_maior_gasto": str(por_categoria.index[0]),
                            "valor_maior_gasto": float(por_categoria.iloc[0]),
                            "categoria_menor_gasto": str(por_categoria.index[-1]),
                            "valor_menor_gasto": float(por_categoria.iloc[-1]),
                            "concentracao_top_3": round((top_3_sum / total_despesas * 100), 2) if total_despesas > 0 else 0
                        }
                    else:
                        context = {"erro": "Nenhuma despesa encontrada"}
                else:
                    context = {"erro": "Nenhuma despesa no período"}
                    
            elif chart_type == "distribuicao_percentual":
                # Análise específica para gráfico de distribuição
                context = {
                    "tipo_analise": "distribuição percentual",
                    "total_registros": len(df_filtrado),
                    "categorias_unicas": len(df_filtrado['Categoria'].unique()),
                    "tipo_mais_frequente": str(df_filtrado['Tipo'].value_counts().index[0]) if not df_filtrado.empty else "N/A"
                }
            
            return context
            
        except Exception as e:
            return {"erro": f"Erro ao preparar contexto do gráfico: {str(e)}"}
    
    def generate_chart_insights(self, chart_data, chart_type, df_filtrado=None, custom_question=None):
        """Gera insights ou responde pergunta sobre um gráfico/tabela específico.

        Args:
            chart_data (dict|list): Dados preparados da visualização.
            chart_type (str): Identificador (ex: 'rentabilidade', 'liquidez', 'indicadores').
            df_filtrado (pd.DataFrame, opcional): DataFrame para gerar alertas/narrativa.
            custom_question (str, opcional): Pergunta do usuário. Se None gera análise padrão.
        """
        if not self.is_available():
            return "IA não disponível. Configure a API key."
        try:
            serial_chart = self._convert_to_serializable(chart_data)
            alerts, narrativa = ([], None)
            if isinstance(df_filtrado, pd.DataFrame) and not df_filtrado.empty:
                alerts, narrativa = self._build_executive_alerts_and_narrative(df_filtrado)
            alerts_texto = "; ".join([f"[{a['nivel'].upper()}] {a['mensagem']}" for a in alerts]) if alerts else "Nenhum alerta relevante."
            base_context_json = json.dumps({
                "chart_type": chart_type,
                "chart_data": serial_chart,
                "executive_alerts": alerts,
                "executive_narrative": narrativa
            }, indent=2, ensure_ascii=False)
            if custom_question:
                prompt = f"""
Você é um analista financeiro sênior. Responda de forma objetiva e executiva à pergunta sobre a visualização selecionada.

TIPO DE VISUALIZAÇÃO: {chart_type}
ALERTAS EXECUTIVOS: {alerts_texto}
NARRATIVA EXECUTIVA (se houver): {narrativa if narrativa else 'N/A'}
DADOS DA VISUALIZAÇÃO (JSON):
{base_context_json}

PERGUNTA DO USUÁRIO:
{custom_question}

INSTRUÇÕES:
1. Se existirem alertas críticos, trate-os primeiro.
2. Cite números/chaves relevantes do chart_data (não invente valores).
3. Forneça implicações estratégicas.
4. Termine com 1-2 recomendações práticas.
Responda em português brasileiro, formato conciso.
"""
            else:
                prompt = f"""
Você é um analista financeiro sênior. Gere uma análise executiva da visualização.

TIPO DE VISUALIZAÇÃO: {chart_type}
ALERTAS EXECUTIVOS: {alerts_texto}
NARRATIVA EXECUTIVA (se houver): {narrativa if narrativa else 'N/A'}
DADOS DA VISUALIZAÇÃO (JSON):
{base_context_json}

Produza:
- Resumo objetivo (1 frase)
- 2-4 destaques quantitativos
- Riscos / atenções (se houver)
- Próxima ação recomendada
Responda em português brasileiro.
"""
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Erro na análise do gráfico: {e}"
    
    def generate_metric_insights(self, metric_data, metric_id, df_filtrado=None, custom_question=None):
        """Gera insights ou responde pergunta sobre uma métrica específica.

        Args:
            metric_data (dict): Dados preparados da métrica.
            metric_id (str): Identificador da métrica.
            df_filtrado (pd.DataFrame, opcional): DataFrame para contexto adicional.
            custom_question (str, opcional): Pergunta do usuário. Se None gera análise padrão.
        """
        if not self.is_available():
            return "IA não disponível. Configure a API key."
        try:
            serial_metric = self._convert_to_serializable(metric_data)
            
            # Gerar contexto executivo se DataFrame disponível
            alerts, narrativa = ([], None)
            if isinstance(df_filtrado, pd.DataFrame) and not df_filtrado.empty:
                alerts, narrativa = self._build_executive_alerts_and_narrative(df_filtrado)
            
            alerts_texto = "; ".join([f"[{a['nivel'].upper()}] {a['mensagem']}" for a in alerts]) if alerts else "Nenhum alerta relevante."
            
            base_context_json = json.dumps({
                "metric_id": metric_id,
                "metric_data": serial_metric,
                "executive_alerts": alerts,
                "executive_narrative": narrativa
            }, indent=2, ensure_ascii=False)
            
            if custom_question:
                prompt = f"""
Você é um analista financeiro sênior. Responda de forma objetiva e executiva à pergunta sobre a métrica selecionada.

MÉTRICA: {metric_id}
ALERTAS EXECUTIVOS: {alerts_texto}
NARRATIVA EXECUTIVA (se houver): {narrativa if narrativa else 'N/A'}
DADOS DA MÉTRICA (JSON):
```json
{base_context_json}
```

PERGUNTA DO USUÁRIO: {custom_question}

Responda de forma clara, técnica mas acessível. Use dados específicos dos números quando relevante. Se houver tendências, riscos ou oportunidades, destaque-os.
"""
            else:
                prompt = f"""
Você é um analista financeiro sênior. Analise esta métrica financeira específica e forneça insights executivos.

MÉTRICA: {metric_id}
ALERTAS EXECUTIVOS: {alerts_texto}
DADOS DA MÉTRICA (JSON):
```json
{base_context_json}
```

Forneça uma análise estruturada contendo:

## 📊 ANÁLISE DA MÉTRICA
- Valor atual e evolução histórica
- Comparação com período anterior
- Tendência identificada

## 🎯 BENCHMARKS E INTERPRETAÇÃO
- Como interpretar estes valores
- Comparação com boas práticas do mercado
- Se está em nível adequado, alto ou baixo

## ⚠️ INSIGHTS E RECOMENDAÇÕES
- Principais achados desta métrica
- Riscos ou oportunidades identificados
- Ações recomendadas baseadas nos dados

Use dados específicos dos números. Seja objetivo e foque em insights acionáveis.
"""
            
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Erro na análise da métrica: {e}"
    
    def analyze_all_charts(self, df, df_filtrado, kpis):
        """
        Analisa todos os gráficos de uma vez e fornece insights integrados
        """
        if not self.is_available():
            return "IA não disponível."
        
        try:
            # Preparar dados para cada tipo de gráfico
            evolucao_data = self._prepare_evolution_data(df_filtrado)
            despesas_data = self._prepare_expenses_data(df_filtrado)
            distribuicao_data = self._prepare_distribution_data(df_filtrado)
            
            # Preparar contexto completo
            full_context = self.prepare_data_context(df, df_filtrado, kpis)
            
            prompt = f"""
            Você é um consultor financeiro sênior. Analise todos os gráficos do dashboard e forneça uma análise integrada e estratégica.

            DADOS DOS GRÁFICOS:
            
            1. GRÁFICO DE EVOLUÇÃO TEMPORAL:
            {json.dumps(evolucao_data, indent=2, ensure_ascii=False)}
            
            2. GRÁFICO DE DESPESAS POR CATEGORIA:
            {json.dumps(despesas_data, indent=2, ensure_ascii=False)}
            
            3. GRÁFICO DE DISTRIBUIÇÃO PERCENTUAL:
            {json.dumps(distribuicao_data, indent=2, ensure_ascii=False)}
            
            CONTEXTO COMPLETO:
            {json.dumps(full_context, indent=2, ensure_ascii=False)}

            Forneça uma análise executiva estruturada contendo:

            ## 📊 RESUMO EXECUTIVO
            - Visão geral do desempenho financeiro
            - Principais destaques dos gráficos

            ## 📈 ANÁLISE TEMPORAL DETALHADA
            - Melhor e pior mês em receitas
            - Tendências de crescimento ou declínio
            - Sazonalidade identificada

            ## 💸 ANÁLISE DE DESPESAS
            - Categorias com maior impacto
            - Oportunidades de otimização
            - Alertas de gastos elevados

            ## 🎯 INSIGHTS ESTRATÉGICOS
            - Oportunidades de crescimento
            - Riscos identificados
            - Recomendações específicas

            ## 📋 PLANO DE AÇÃO
            - 3 ações prioritárias baseadas nos dados
            - Métricas para acompanhar
            - Próximos passos recomendados

            Seja específico, use números dos dados e forneça insights acionáveis em português brasileiro.
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Erro na análise integrada: {str(e)}"
    
    def _prepare_evolution_data(self, df_filtrado):
        """Prepara dados do gráfico de evolução"""
        try:
            if df_filtrado.empty:
                return {"erro": "Nenhum dado disponível"}
                
            df_temp = df_filtrado.copy()
            df_temp['Mes_Ano'] = df_temp['Data'].dt.strftime('%m/%Y')
            
            # Agrupar por mês e tipo
            evolucao = df_temp.groupby(['Mes_Ano', 'Tipo'])['Valor'].sum().unstack(fill_value=0)
            
            # Converter para dicionário com chaves seguras
            resultado = {}
            for mes in evolucao.index:
                resultado[str(mes)] = {}
                for tipo in evolucao.columns:
                    resultado[str(mes)][str(tipo)] = float(evolucao.loc[mes, tipo])
            
            return resultado
            
        except Exception as e:
            return {"erro": f"Erro ao preparar dados de evolução: {str(e)}"}
    
    def _prepare_expenses_data(self, df_filtrado):
        """Prepara dados do gráfico de despesas"""
        try:
            despesas = df_filtrado[df_filtrado['Tipo'] == 'Despesa']
            if despesas.empty:
                return {"erro": "Nenhuma despesa encontrada"}
                
            por_categoria = despesas.groupby('Categoria')['Valor'].sum().sort_values(ascending=False)
            
            # Converter para dicionário com chaves string
            resultado = {}
            for categoria, valor in por_categoria.items():
                resultado[str(categoria)] = float(valor)
                
            return resultado
            
        except Exception as e:
            return {"erro": f"Erro ao preparar dados de despesas: {str(e)}"}
    
    def _prepare_distribution_data(self, df_filtrado):
        """Prepara dados do gráfico de distribuição"""
        try:
            if df_filtrado.empty:
                return {"erro": "Nenhum dado disponível"}
                
            distribuicao = df_filtrado.groupby(['Tipo', 'Categoria'])['Valor'].sum()
            
            # Converter para dicionário com chaves string
            resultado = {}
            for (tipo, categoria), valor in distribuicao.items():
                chave = f"{str(tipo)}_{str(categoria)}"
                resultado[chave] = float(valor)
                
            return resultado
            
        except Exception as e:
            return {"erro": f"Erro ao preparar dados de distribuição: {str(e)}"}
    
    def suggest_questions(self, context):
        """
        Sugere perguntas relevantes baseadas nos dados
        """
        if not self.is_available():
            return []
        
        try:
            # O contexto já deve estar serializável, mas vamos garantir
            serializable_context = self._convert_to_serializable(context)
            
            prompt = f"""
            Com base nos dados fornecidos, sugira 5 perguntas relevantes que um usuário poderia fazer para obter insights valiosos.

            CONTEXTO DOS DADOS:
            {json.dumps(serializable_context, indent=2, ensure_ascii=False)}

            Sugira perguntas que:
            1. Explorem tendências temporais
            2. Analisem categorias específicas
            3. Comparem períodos
            4. Identifiquem oportunidades ou riscos
            5. Forneçam insights estratégicos

            Retorne apenas as perguntas, uma por linha, em português brasileiro.
            """
            
            response = self.model.generate_content(prompt)
            questions = [q.strip() for q in response.text.split('\n') if q.strip()]
            return questions[:5]  # Limitar a 5 perguntas
            
        except Exception as e:
            return [f"Erro ao gerar sugestões: {str(e)}"]

# Função para criar interface de IA no Streamlit
def create_ai_interface(df, df_filtrado, kpis):
    """
    Cria a interface de IA no Streamlit
    """
    st.markdown("---")
    st.subheader("🤖 Análise Inteligente com IA")
    
    # Inicializar analisador de IA
    analyzer = AIAnalyzer()
    
    if not analyzer.is_available():
        st.error("❌ API do Google Gemini não configurada!")
        st.info("""
        Para usar a análise de IA:
        1. Obtenha uma API key em: https://makersuite.google.com/app/apikey
        2. Crie um arquivo `.env` na raiz do projeto
        3. Adicione: `GOOGLE_GEMINI_API_KEY=sua_chave_aqui`
        """)
        return
    
    # Tabs para diferentes funcionalidades
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Insights Automáticos", "❓ Fazer Pergunta", "💡 Sugestões", "🔍 Análise Integrada"])
    
    with tab1:
        st.write("**Análise automática dos dados atuais:**")
        if st.button("🔍 Gerar Insights Automáticos", type="primary"):
            import time
            
            # Criar placeholder para animação
            status_placeholder = st.empty()
            progress_bar = st.progress(0)
            
            # Animação de carregamento
            for i in range(100):
                if i < 30:
                    status_placeholder.info("🔍 Analisando dados...")
                elif i < 60:
                    status_placeholder.info("🤖 IA processando informações...")
                elif i < 90:
                    status_placeholder.info("📊 Gerando insights...")
                else:
                    status_placeholder.info("✨ Finalizando análise...")
                
                progress_bar.progress(i + 1)
                time.sleep(0.025)  # 2.5 segundos total
            
            # Gerar insights
            insights = analyzer.generate_insights(df, df_filtrado, kpis)
            
            # Limpar animação
            status_placeholder.empty()
            progress_bar.empty()
            
            # Mostrar resultado em expander organizado
            with st.expander("📈 **Insights Gerados pela IA** - Clique para expandir", expanded=True):
                st.markdown("---")
                st.markdown("### 🤖 Análise Automática dos Dados")
                st.markdown(f"**Data da análise:** {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
                st.markdown("---")
                st.markdown(insights)
                st.markdown("---")
                st.info("💡 **Dica:** Você pode fazer perguntas específicas na aba 'Fazer Pergunta' para obter insights mais direcionados.")
    
    with tab2:
        st.write("**Faça uma pergunta específica sobre os dados:**")
        
        # Campo de pergunta
        user_question = st.text_area(
            "Digite sua pergunta:",
            placeholder="Ex: Qual categoria de despesa tem o maior impacto no orçamento?",
            height=100
        )
        
        if st.button("🤖 Perguntar para IA", type="primary") and user_question:
            import time
            
            # Criar placeholder para animação
            status_placeholder = st.empty()
            progress_bar = st.progress(0)
            
            # Animação de carregamento personalizada para perguntas
            for i in range(100):
                if i < 25:
                    status_placeholder.info("� Processando sua pergunta...")
                elif i < 50:
                    status_placeholder.info("🔍 Analisando dados relacionados...")
                elif i < 75:
                    status_placeholder.info("🤖 IA formulando resposta...")
                else:
                    status_placeholder.info("✨ Finalizando análise...")
                
                progress_bar.progress(i + 1)
                time.sleep(0.025)  # 2.5 segundos total
            
            # Gerar resposta
            answer = analyzer.generate_insights(df, df_filtrado, kpis, user_question)
            
            # Limpar animação
            status_placeholder.empty()
            progress_bar.empty()
            
            # Mostrar resultado em container dedicado
            st.markdown("---")
            
            # Container para a conversa
            with st.container():
                # Cabeçalho da conversa
                col1, col2 = st.columns([1, 8])
                with col1:
                    st.markdown("👤")
                with col2:
                    st.markdown(f"**Sua pergunta:** {user_question}")
                
                st.markdown("---")
                
                # Resposta da IA em expander
                with st.expander("💬 **Resposta da IA** - Clique para expandir", expanded=True):
                    col1, col2 = st.columns([1, 8])
                    with col1:
                        st.markdown("🤖")
                    with col2:
                        st.markdown(f"**Respondido em:** {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
                    
                    st.markdown("---")
                    st.markdown(answer)
                    st.markdown("---")
                    
                    # Botões de ação
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("🔄 Nova Pergunta", key="new_question"):
                            st.rerun()
                    with col2:
                        if st.button("📊 Ver Dados", key="show_data"):
                            st.info("Os dados estão disponíveis na seção 'Dados Detalhados' no final da página.")
                    with col3:
                        if st.button("💡 Sugestões", key="go_suggestions"):
                            st.info("Confira a aba 'Sugestões' para mais ideias de perguntas.")
        
        # Seção de perguntas frequentes
        st.markdown("---")
        st.markdown("### 💭 Perguntas Frequentes")
        
        perguntas_exemplo = [
            "Qual foi o mês que teve mais receita?",
            "Em que categoria devo focar para reduzir despesas?",
            "Como foi a tendência nos últimos 3 meses?",
            "Compare o primeiro e último mês dos dados",
            "Qual categoria está crescendo mais rapidamente?"
        ]
        
        st.markdown("**Experimente perguntas como:**")
        for i, pergunta in enumerate(perguntas_exemplo):
            if st.button(f"❓ {pergunta}", key=f"freq_{i}"):
                st.text_area("Pergunta selecionada:", value=pergunta, height=50, key="selected_question")
    
    with tab3:
        st.write("**Perguntas sugeridas pela IA:**")
        
        if st.button("💡 Gerar Sugestões", type="secondary"):
            import time
            
            # Criar placeholder para animação
            status_placeholder = st.empty()
            progress_bar = st.progress(0)
            
            # Animação de carregamento para sugestões
            for i in range(100):
                if i < 25:
                    status_placeholder.info("� IA analisando contexto...")
                elif i < 50:
                    status_placeholder.info("💡 Gerando perguntas relevantes...")
                elif i < 75:
                    status_placeholder.info("🎯 Refinando sugestões...")
                else:
                    status_placeholder.info("✨ Preparando lista...")
                
                progress_bar.progress(i + 1)
                time.sleep(0.025)  # 2.5 segundos total
            
            # Gerar sugestões
            context = analyzer.prepare_data_context(df, df_filtrado, kpis)
            suggestions = analyzer.suggest_questions(context)
            
            # Limpar animação
            status_placeholder.empty()
            progress_bar.empty()
            
            # Mostrar resultado em expander organizado
            with st.expander("🎯 **Perguntas Sugeridas pela IA** - Clique para expandir", expanded=True):
                st.markdown("---")
                st.markdown("### 💡 Sugestões Personalizadas")
                st.markdown(f"**Gerado em:** {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
                st.markdown("---")
                
                for i, question in enumerate(suggestions, 1):
                    col1, col2 = st.columns([1, 8])
                    with col1:
                        st.markdown(f"**{i}.**")
                    with col2:
                        st.markdown(question)
                        if st.button(f"🔍 Perguntar isso", key=f"suggest_{i}"):
                            st.info(f"💡 Vá para a aba 'Fazer Pergunta' e digite: '{question}'")
                
                st.markdown("---")
                st.info("💡 **Como usar:** Clique em 'Perguntar isso' ou copie uma pergunta para a aba 'Fazer Pergunta'")
    
    with tab4:
        st.write("**Análise integrada de todos os gráficos do dashboard:**")
        st.info("🎯 Esta análise combina todos os gráficos para fornecer insights estratégicos completos")
        
        if st.button("🔍 Analisar Todos os Gráficos", type="primary"):
            import time
            
            # Criar placeholder para animação
            status_placeholder = st.empty()
            progress_bar = st.progress(0)
            
            # Animação de carregamento específica para análise integrada
            for i in range(100):
                if i < 20:
                    status_placeholder.info("📊 Coletando dados dos gráficos...")
                elif i < 40:
                    status_placeholder.info("📈 Analisando evolução temporal...")
                elif i < 60:
                    status_placeholder.info("💸 Examinando despesas por categoria...")
                elif i < 80:
                    status_placeholder.info("🔍 Identificando padrões e tendências...")
                else:
                    status_placeholder.info("🎯 Gerando insights estratégicos...")
                
                progress_bar.progress(i + 1)
                time.sleep(0.025)  # 2.5 segundos total
            
            # Gerar análise integrada
            integrated_analysis = analyzer.analyze_all_charts(df, df_filtrado, kpis)
            
            # Limpar animação
            status_placeholder.empty()
            progress_bar.empty()
            
            # Mostrar resultado em seção dedicada
            with st.expander("🎯 **Análise Estratégica Integrada** - Clique para expandir", expanded=True):
                st.markdown("---")
                st.markdown("### 🔍 Análise Completa dos Gráficos")
                st.markdown(f"**Análise realizada em:** {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
                st.markdown("**Gráficos analisados:** Evolução Temporal, Despesas por Categoria, Distribuição Percentual")
                st.markdown("---")
                st.markdown(integrated_analysis)
                st.markdown("---")
                
                # Seção de ações recomendadas
                st.markdown("### 🚀 Ações Rápidas")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📊 Ver KPIs", key="show_kpis"):
                        st.info("Os KPIs principais estão no topo da página.")
                
                with col2:
                    if st.button("📈 Analisar Gráfico", key="analyze_specific"):
                        st.info("Use os botões 'Analisar Este Gráfico' em cada visualização.")
                
                with col3:
                    if st.button("❓ Fazer Pergunta", key="ask_specific"):
                        st.info("Vá para a aba 'Fazer Pergunta' para insights específicos.")
            
            # Adicionar seção de perguntas sugeridas baseadas na análise
            st.markdown("---")
            st.markdown("### 💭 Perguntas Específicas Sugeridas")
            st.info("**Com base na análise integrada, você pode fazer perguntas como:**")
            
            perguntas_sugeridas = [
                "Qual foi o mês com maior receita e o que causou esse pico?",
                "Em que categoria devo focar para reduzir despesas?", 
                "Qual é a tendência de crescimento dos últimos 3 meses?",
                "Como o desempenho deste trimestre se compara ao anterior?",
                "Quais são os 3 maiores riscos financeiros identificados?"
            ]
            
            for i, pergunta in enumerate(perguntas_sugeridas, 1):
                col1, col2 = st.columns([1, 8])
                with col1:
                    st.markdown(f"**{i}.**")
                with col2:
                    if st.button(pergunta, key=f"integrated_q_{i}"):
                        st.info(f"💡 Vá para a aba 'Fazer Pergunta' e digite: '{pergunta}'")

# Função para análise de gráficos específicos
def analyze_chart_with_ai(chart_data, chart_type, chart_title):
    """
    Analisa um gráfico específico com IA
    """
    analyzer = AIAnalyzer()
    
    if not analyzer.is_available():
        st.error("❌ IA não disponível para análise de gráficos")
        return None
    
    try:
        insights = analyzer.generate_chart_insights(chart_data, chart_type)
        return insights
    except Exception as e:
        st.error(f"Erro na análise do gráfico: {str(e)}")
        return None