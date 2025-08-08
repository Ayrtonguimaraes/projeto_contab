"""
Página do Dashboard Executivo
"""

import streamlit as st
from pages.base_page import BasePage
import plotly.graph_objects as go

class DashboardExecutivoPage(BasePage):
    """Página principal do dashboard executivo"""
    
    def render(self):
        """Renderiza a página do dashboard executivo (Etapa 1 melhoria: seletor de categoria + blocos)"""
        st.title("🏠 Dashboard Executivo")
        top_l, top_r = st.columns([0.65,0.35])
        with top_l:
            st.markdown("### Visão Geral Estratégica")
        with top_r:
            categoria = self._render_categoria_selector()
        st.markdown("---")
        
        # KPIs principais
        self._render_kpis()
        
        # Alertas e narrativa (novos)
        alerts = self._generate_alerts()
        self._render_alerts(alerts)
        self._render_narrativa(alerts)
        st.markdown("---")
        
        # Bloco por categoria
        self._render_categoria_block(categoria)
        
        # Sidebar info
        self.render_sidebar_info()
    
    # -------------------- UI Categoria --------------------
    def _render_categoria_selector(self):
        return st.selectbox(
            "Categoria Analítica",
            ["Liquidez","Endividamento","Rentabilidade","Ciclos"],
            key="dash_cat"
        )
    
    # -------------------- KPIs ----------------------------
    def _render_kpis(self):
        """KPIs principais (mantido, pode ser refinado em etapas futuras)"""
        st.subheader("📈 KPIs Principais")
        try:
            kpis = self.analyzer.get_kpis_principais()
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "💰 Receita Líquida", 
                    f"R$ {kpis['receita_liquida']['atual']:,.0f}".replace(',', '.'),
                    f"{kpis['receita_liquida']['variacao']:+.1f}%"
                )
                st.metric(
                    "📈 ROE", 
                    f"{kpis['roe']['atual']:.1%}",
                    f"{kpis['roe']['variacao']:+.1f}pp"
                )
            with col2:
                st.metric(
                    "💎 Lucro Líquido", 
                    f"R$ {kpis['lucro_liquido']['atual']:,.0f}".replace(',', '.'),
                    f"{kpis['lucro_liquido']['variacao']:+.1f}%"
                )
                st.metric(
                    "🎯 ROA", 
                    f"{kpis['roa']['atual']:.1%}",
                    f"{kpis['roa']['variacao']:+.1f}pp"
                )
            with col3:
                st.metric(
                    "💧 Margem Líquida", 
                    f"{kpis['margem_liquida']['atual']:.1%}",
                    f"{kpis['margem_liquida']['variacao']:+.1f}pp"
                )
                st.metric(
                    "🛡️ Liquidez Corrente", 
                    f"{kpis['liquidez_corrente']['atual']:.2f}",
                    f"{kpis['liquidez_corrente']['variacao']:+.1f}%"
                )
        except Exception as e:
            self.show_error(f"Erro ao carregar KPIs: {str(e)}")
    
    # -------------------- Bloco Categoria -----------------
    def _render_categoria_block(self, categoria: str):
        if categoria == "Liquidez":
            self._render_liquidez_block()
        elif categoria == "Endividamento":
            self._render_endividamento_block()
        elif categoria == "Rentabilidade":
            self._render_rentabilidade_block()
        elif categoria == "Ciclos":
            self._render_ciclos_block()
    
    # -------------------- Liquidez ------------------------
    def _render_liquidez_block(self):
        st.subheader("🛡️ Liquidez - Zona de Segurança & Sensibilidades")
        df = self.analyzer.df
        required = ['Ano','Liquidez Corrente (LC) ','Liquidez Imediata (LI)','Caixa e Equivalentes de Caixa']
        if not all(c in df.columns for c in required):
            st.warning("Colunas de liquidez ausentes para análise detalhada.")
            return
        anos = df['Ano']
        lc = df['Liquidez Corrente (LC) ']
        li = df['Liquidez Imediata (LI)']
        fig = go.Figure()
        # Zona de segurança (1.0 - 2.0)
        fig.add_hrect(y0=1.0, y1=2.0, fillcolor="lightgreen", opacity=0.25, line_width=0)
        fig.add_trace(go.Scatter(x=anos, y=lc, mode='lines+markers', name='Liquidez Corrente', line=dict(color='#1f77b4', width=3)))
        fig.add_trace(go.Scatter(x=anos, y=li, mode='lines+markers', name='Liquidez Imediata', line=dict(color='#ff7f0e', width=3)))
        fig.update_layout(title="Liquidez Corrente vs Zona de Segurança", height=420, legend=dict(orientation='h', yanchor='bottom', y=1.02, x=0))
        st.plotly_chart(fig, use_container_width=True)
        # Insight rápido
        if len(anos) >= 2:
            delta_li = li.iloc[-1] - li.iloc[-2]
            if delta_li < 0:
                st.info(f"🔍 Queda de {abs(delta_li):.2f} na Liquidez Imediata no último período — investigar redução de caixa ou aumento de passivos de curtíssimo prazo.")
    
    # -------------------- Endividamento -------------------
    def _render_endividamento_block(self):
        st.subheader("🏦 Estrutura de Endividamento - Composição 100%")
        df = self.analyzer.df
        required = ['Ano','Passivo Circulante','Passivo Não Circulante']
        if not all(c in df.columns for c in required):
            st.warning("Colunas de passivos ausentes.")
            return
        data = df[['Ano','Passivo Circulante','Passivo Não Circulante']].copy()
        data['Total Passivos'] = data['Passivo Circulante'] + data['Passivo Não Circulante']
        data['Curto %'] = data['Passivo Circulante'] / data['Total Passivos'] * 100
        data['Longo %'] = data['Passivo Não Circulante'] / data['Total Passivos'] * 100
        fig = go.Figure()
        fig.add_bar(name='Curto Prazo', x=data['Ano'], y=data['Curto %'], marker_color='#ff9999')
        fig.add_bar(name='Longo Prazo', x=data['Ano'], y=data['Longo %'], marker_color='#66b3ff')
        fig.update_layout(barmode='stack', yaxis=dict(ticksuffix='%'), title='Composição da Dívida (100%)', height=420)
        st.plotly_chart(fig, use_container_width=True)
        # Linha EG se existir
        if 'Endividamento Geral (EG)' in df.columns:
            eg_fig = go.Figure()
            eg_fig.add_trace(go.Scatter(x=df['Ano'], y=df['Endividamento Geral (EG)'], mode='lines+markers', name='EG', line=dict(color='#333', width=3)))
            eg_fig.update_layout(title='Evolução do Endividamento Geral', height=300)
            st.plotly_chart(eg_fig, use_container_width=True)
    
    # -------------------- Rentabilidade (DuPont) ----------
    def _render_rentabilidade_block(self):
        st.subheader("📈 Rentabilidade - Visão DuPont Integrada")
        df = self.analyzer.df
        required = ['Ano','Margem Líquida (ML)','Giro do Ativo (GA)','Multiplicador de Alavancagem Financeira (MAF)','Rentabilidade do Patrimônio Líquido (ROE) ']
        if not all(c in df.columns for c in required):
            st.warning("Colunas de rentabilidade/duPont ausentes.")
            return
        anos = df['Ano']
        margem = df['Margem Líquida (ML)']
        giro = df['Giro do Ativo (GA)']
        maf = df['Multiplicador de Alavancagem Financeira (MAF)']
        roe = df['Rentabilidade do Patrimônio Líquido (ROE) ']
        # Scatter de movimento
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=margem, y=giro, mode='markers+text', text=[str(a) for a in anos],
            marker=dict(size=(maf*12).clip(10,50), color=roe, colorscale='RdYlGn', showscale=True, colorbar=dict(title='ROE')),
            textposition='top center', name='Margem x Giro'
        ))
        # Seta entre últimos dois períodos
        if len(anos) >= 2:
            fig.add_annotation(
                ax=margem.iloc[-2], ay=giro.iloc[-2],
                x=margem.iloc[-1], y=giro.iloc[-1],
                showarrow=True, arrowhead=3, arrowsize=1.2,
                arrowcolor='#444'
            )
        fig.update_layout(xaxis_title='Margem Líquida', yaxis_title='Giro do Ativo', title='Mapa Margem x Giro (Tamanho = MAF; Cor = ROE)', height=460)
        st.plotly_chart(fig, use_container_width=True)
        # Decomposição impacto (% var ROE atribuída)
        if len(anos) >= 2:
            import numpy as np
            m_var = margem.iloc[-1] - margem.iloc[-2]
            g_var = giro.iloc[-1] - giro.iloc[-2]
            maf_var = maf.iloc[-1] - maf.iloc[-2]
            # Aproximação efeito multiplicativo (derivada log): dROE/ROE ≈ dM/M + dG/G + dMAF/MAF
            contrib = {}
            for label, cur, var in [("Margem", margem.iloc[-1], m_var),("Giro", giro.iloc[-1], g_var),("Alavancagem", maf.iloc[-1], maf_var)]:
                try:
                    contrib[label] = (var / cur) if cur not in (0,None) else 0
                except: contrib[label]=0
            total = sum(contrib.values()) or 1
            rows = [(k, v/total*100) for k,v in contrib.items()]
            rows_sorted = sorted(rows, key=lambda x: abs(x[1]), reverse=True)
            st.markdown("**Impacto Relativo Estimado na Variação do ROE**")
            for k,pct in rows_sorted:
                st.write(f"- {k}: {pct:+.1f}% da variação relativa")
    
    # -------------------- Ciclos / Prazos -----------------
    def _render_ciclos_block(self):
        st.subheader("⏱️ Ciclo Financeiro - Waterfall")
        df = self.analyzer.df
        required = ['Ano','Prazo Médio de Renovação dos Estoques (PMRE) ','Prazo Médio de Recebimento das Vendas (PMRV) ','Prazo Médio de Pagamento das Compras (PMPC) ','Ciclo Operacional e Ciclo Financeiro']
        if not all(c in df.columns for c in required):
            st.warning("Colunas de ciclo ausentes.")
            return
        # Usar último ano
        last = df.sort_values('Ano').iloc[-1]
        pmre = last['Prazo Médio de Renovação dos Estoques (PMRE) ']
        pmrv = last['Prazo Médio de Recebimento das Vendas (PMRV) ']
        pmpc = last['Prazo Médio de Pagamento das Compras (PMPC) ']
        ciclo_fin = last['Ciclo Operacional e Ciclo Financeiro']
        # Construção waterfall: PMRE + PMRV - PMPC = Ciclo
        fig = go.Figure(go.Waterfall(
            name='Ciclo',
            orientation='v',
            measure=['relative','relative','relative','total'],
            x=['PMRE','PMRV','- PMPC','Ciclo Financeiro'],
            text=[f"{pmre:.0f}", f"{pmrv:.0f}", f"-{pmpc:.0f}", f"{ciclo_fin:.0f}"],
            y=[pmre, pmrv, -pmpc, ciclo_fin],
            connector={'line': {'color': 'rgba(100,100,100,0.4)'}}
        ))
        fig.update_layout(title=f"Decomposição do Ciclo Financeiro (Ano {int(last['Ano'])})", height=430)
        st.plotly_chart(fig, use_container_width=True)
        # Evolução do ciclo
        evo_fig = go.Figure()
        evo_fig.add_trace(go.Scatter(x=df['Ano'], y=df['Ciclo Operacional e Ciclo Financeiro'], mode='lines+markers', name='Ciclo Financeiro', line=dict(color='#1f77b4', width=3)))
        evo_fig.update_layout(title='Evolução do Ciclo Financeiro', height=300)
        st.plotly_chart(evo_fig, use_container_width=True)
    def _generate_alerts(self):
        """Gera lista de alertas financeiros executivos"""
        alerts = []
        try:
            df = self.analyzer.df.sort_values('Ano')
            if len(df) < 2:
                return alerts
            prev, cur = df.iloc[-2], df.iloc[-1]
            ano_prev, ano_cur = int(df['Ano'].iloc[-2]), int(df['Ano'].iloc[-1])
            def pct_delta(a,b):
                try:
                    return (b-a)/a*100 if a not in (0,None) else None
                except: return None
            # Liquidez Corrente
            if 'Liquidez Corrente (LC) ' in df.columns:
                lc_cur = cur['Liquidez Corrente (LC) ']
                if lc_cur < 1.0:
                    alerts.append(("critico", f"Liquidez Corrente {lc_cur:.2f} abaixo de 1.0 (risco de cobertura de curto prazo)", ano_cur))
                elif lc_cur < 1.2:
                    alerts.append(("atencao", f"Liquidez Corrente {lc_cur:.2f} em zona de atenção (<1.2)", ano_cur))
            # Liquidez Imediata queda
            if 'Liquidez Imediata (LI)' in df.columns:
                li_delta = cur['Liquidez Imediata (LI)'] - prev['Liquidez Imediata (LI)']
                if li_delta < -0.1:
                    alerts.append(("atencao", f"Liquidez Imediata caiu {li_delta:.2f} vs {ano_prev}", ano_cur))
            # Endividamento Geral
            if 'Endividamento Geral (EG)' in df.columns:
                eg_delta_pct = pct_delta(prev['Endividamento Geral (EG)'], cur['Endividamento Geral (EG)'])
                if eg_delta_pct is not None and eg_delta_pct > 10:
                    alerts.append(("atencao", f"Endividamento Geral aumentou {eg_delta_pct:.1f}% vs {ano_prev}", ano_cur))
            # Margem Líquida queda
            if 'Margem Líquida (ML)' in df.columns:
                ml_var_pp = (cur['Margem Líquida (ML)'] - prev['Margem Líquida (ML)'])*100
                if ml_var_pp < -2:
                    alerts.append(("critico", f"Margem Líquida caiu {ml_var_pp:.1f} pp vs {ano_prev}", ano_cur))
            # ROE queda
            if 'Rentabilidade do Patrimônio Líquido (ROE) ' in df.columns:
                roe_var_pp = (cur['Rentabilidade do Patrimônio Líquido (ROE) '] - prev['Rentabilidade do Patrimônio Líquido (ROE) '])*100
                if roe_var_pp < -3:
                    alerts.append(("critico", f"ROE recuou {roe_var_pp:.1f} pp vs {ano_prev}", ano_cur))
        except Exception:
            pass
        return alerts
    def _render_alerts(self, alerts):
        """Mostra alertas priorizando críticos"""
        if not alerts:
            return
        # Ordenar: crítico primeiro
        prioridade = {"critico":0, "atencao":1, "info":2}
        alerts_sorted = sorted(alerts, key=lambda x: prioridade.get(x[0], 9))
        st.subheader("⚠️ Alertas")
        for nivel, msg, ano in alerts_sorted:
            if nivel == 'critico':
                st.error(f"{msg}")
            elif nivel == 'atencao':
                st.warning(f"{msg}")
            else:
                st.info(msg)
    def _render_narrativa(self, alerts):
        """Resumo executivo textual baseado em movimentos chave"""
        df = self.analyzer.df.sort_values('Ano')
        if len(df) < 2:
            return
        prev, cur = df.iloc[-2], df.iloc[-1]
        ano_prev, ano_cur = int(df['Ano'].iloc[-2]), int(df['Ano'].iloc[-1])
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
        # Construir narrativa
        if roe_pct is not None:
            direction = 'recuo' if roe_pct < 0 else 'alta'
            parts.append(f"ROE apresentou {direction} de {abs(roe_pct):.1f}% vs {ano_prev}")
        if ml_pct is not None:
            parts.append(f"Margem Líquida variou {ml_pct:+.1f}%")
        if eg_pct is not None:
            if eg_pct > 0:
                parts.append(f"Endividamento Geral cresceu {eg_pct:.1f}%")
            elif eg_pct < 0:
                parts.append(f"Endividamento Geral reduziu {abs(eg_pct):.1f}%")
        if lc_cur is not None:
            parts.append(f"Liquidez Corrente atual em {lc_cur:.2f}")
        if alerts:
            criticos = [a for a in alerts if a[0]=='critico']
            if criticos:
                parts.append(f"{len(criticos)} alerta(s) crítico(s) demandam ação imediata")
        if not parts:
            return
        st.subheader("📝 Narrativa Executiva")
        st.markdown("; ".join(parts) + ".")
