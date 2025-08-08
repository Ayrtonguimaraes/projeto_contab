"""
Página do Dashboard Executivo
"""

import streamlit as st
from pages.base_page import BasePage
import plotly.graph_objects as go

class DashboardExecutivoPage(BasePage):
    """Página principal do dashboard executivo"""
    
    def render(self):
        """Renderiza a página do dashboard executivo (adiciona modo simplificado)."""
        st.title("🏠 Dashboard Executivo")
        if st.session_state.get('modo_simplificado'):
            self._render_simplified_overview()
            self.render_sidebar_info()
            return
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
        st.subheader("🛡️ Liquidez - Análise de Capacidade de Pagamento")
        df = self.analyzer.df.sort_values('Ano')
        required = ['Ano','Liquidez Corrente (LC) ','Liquidez Imediata (LI)','Caixa e Equivalentes de Caixa']
        if not all(c in df.columns for c in required):
            st.warning("Colunas de liquidez ausentes para análise detalhada.")
            return
            
        if len(df) < 2:
            st.info("Necessário pelo menos 2 anos para análise comparativa de liquidez.")
            return
            
        prev, cur = df.iloc[-2], df.iloc[-1]
        ano_prev, ano_cur = int(prev['Ano']), int(cur['Ano'])
        
        # ----- Tabela de componentes da liquidez -----
        import pandas as pd
        
        # Buscar componentes se disponíveis
        ativo_circ_cols = ['Caixa e Equivalentes de Caixa', 'Contas a Receber (Circulante)', 'Estoques']
        passivo_circ_col = 'Passivo Circulante'
        
        liquidez_data = []
        
        # Liquidez Corrente
        lc_prev, lc_cur = prev['Liquidez Corrente (LC) '], cur['Liquidez Corrente (LC) ']
        delta_lc = lc_cur - lc_prev
        liquidez_data.append({
            'Indicador': 'Liquidez Corrente',
            f'{ano_prev}': f"{lc_prev:.2f}",
            f'{ano_cur}': f"{lc_cur:.2f}",
            'Δ': f"{delta_lc:+.2f}",
            'Status': '🔴 Crítico' if lc_cur < 1.0 else '🟡 Atenção' if lc_cur < 1.2 else '🟢 Adequado',
            'Meta': '≥ 1.20'
        })
        
        # Liquidez Imediata  
        li_prev, li_cur = prev['Liquidez Imediata (LI)'], cur['Liquidez Imediata (LI)']
        delta_li = li_cur - li_prev
        liquidez_data.append({
            'Indicador': 'Liquidez Imediata',
            f'{ano_prev}': f"{li_prev:.2f}",
            f'{ano_cur}': f"{li_cur:.2f}",
            'Δ': f"{delta_li:+.2f}",
            'Status': '🔴 Crítico' if li_cur < 0.15 else '🟡 Atenção' if li_cur < 0.30 else '🟢 Adequado',
            'Meta': '≥ 0.30'
        })
        
        # Liquidez Geral se disponível
        if 'Liquidez Geral (LG)' in df.columns:
            lg_prev, lg_cur = prev['Liquidez Geral (LG)'], cur['Liquidez Geral (LG)']
            delta_lg = lg_cur - lg_prev
            liquidez_data.append({
                'Indicador': 'Liquidez Geral',
                f'{ano_prev}': f"{lg_prev:.2f}",
                f'{ano_cur}': f"{lg_cur:.2f}",
                'Δ': f"{delta_lg:+.2f}",
                'Status': '🔴 Crítico' if lg_cur < 1.0 else '🟡 Atenção' if lg_cur < 1.1 else '🟢 Adequado',
                'Meta': '≥ 1.10'
            })
        
        liquidez_df = pd.DataFrame(liquidez_data)
        st.dataframe(liquidez_df, use_container_width=True, hide_index=True)
        
        # ----- Gráficos lado a lado -----
        col1, col2 = st.columns(2)
        
        with col1:
            # Slope charts focados (sem zona gigante irrelevante)
            fig_slope = go.Figure()
            
            # LC
            fig_slope.add_trace(go.Scatter(
                x=[ano_prev, ano_cur], 
                y=[lc_prev, lc_cur], 
                mode='lines+markers+text',
                text=[f"{lc_prev:.2f}", f"{lc_cur:.2f}"],
                textposition='top center',
                line=dict(color='#3498db', width=4),
                marker=dict(size=10),
                name='Liquidez Corrente'
            ))
            
            # LI (escala secundária)
            fig_slope.add_trace(go.Scatter(
                x=[ano_prev, ano_cur], 
                y=[li_prev, li_cur], 
                mode='lines+markers+text',
                text=[f"{li_prev:.2f}", f"{li_cur:.2f}"],
                textposition='bottom center',
                line=dict(color='#e74c3c', width=4),
                marker=dict(size=10),
                name='Liquidez Imediata',
                yaxis='y2'
            ))
            
            # Linha de referência LC
            fig_slope.add_hline(y=1.0, line_dash="dash", line_color="red", opacity=0.7)
            fig_slope.add_annotation(x=ano_cur, y=1.0, text="Meta LC: 1.0", showarrow=False, yshift=10)
            
            fig_slope.update_layout(
                title='Evolução dos Indicadores de Liquidez',
                height=400,
                yaxis=dict(title='Liquidez Corrente', side='left'),
                yaxis2=dict(title='Liquidez Imediata', side='right', overlaying='y'),
                legend=dict(orientation='h', yanchor='bottom', y=1.02, x=0)
            )
            st.plotly_chart(fig_slope, use_container_width=True)
        
        with col2:
            # Composição do Ativo Circulante (se dados disponíveis)
            if all(col in df.columns for col in ativo_circ_cols) and passivo_circ_col in df.columns:
                caixa_cur = cur['Caixa e Equivalentes de Caixa']
                receber_cur = cur['Contas a Receber (Circulante)'] if 'Contas a Receber (Circulante)' in df.columns else 0
                estoque_cur = cur['Estoques'] if 'Estoques' in df.columns else 0
                passivo_cur = cur[passivo_circ_col]
                
                labels = ['Caixa', 'A Receber', 'Estoques', 'Passivo Circulante']
                values = [caixa_cur, receber_cur, estoque_cur, -passivo_cur]  # Passivo negativo
                colors = ['#2ecc71', '#f39c12', '#9b59b6', '#e74c3c']
                
                fig_comp = go.Figure()
                fig_comp.add_bar(
                    x=labels, 
                    y=values,
                    marker_color=colors,
                    text=[f"R$ {abs(v):,.0f}".replace(',', '.') for v in values],
                    textposition='auto'
                )
                fig_comp.add_hline(y=0, line_color="black", line_width=1)
                fig_comp.update_layout(
                    title=f'Composição da Liquidez ({ano_cur})',
                    height=400,
                    yaxis_title='Valor (R$)',
                    yaxis=dict(tickformat=',.0f')
                )
                st.plotly_chart(fig_comp, use_container_width=True)
            else:
                # Gráfico de barras simples LC vs LI
                fig_bars = go.Figure()
                fig_bars.add_bar(
                    name='Liquidez Corrente',
                    x=[str(ano_prev), str(ano_cur)],
                    y=[lc_prev, lc_cur],
                    marker_color='#3498db',
                    text=[f"{lc_prev:.2f}", f"{lc_cur:.2f}"],
                    textposition='auto'
                )
                fig_bars.add_bar(
                    name='Liquidez Imediata',
                    x=[str(ano_prev), str(ano_cur)],
                    y=[li_prev, li_cur],
                    marker_color='#e74c3c',
                    text=[f"{li_prev:.2f}", f"{li_cur:.2f}"],
                    textposition='auto'
                )
                fig_bars.update_layout(
                    title='Comparação dos Indicadores',
                    height=400,
                    barmode='group'
                )
                st.plotly_chart(fig_bars, use_container_width=True)
        
        # ----- Análise de risco e insights -----
        st.markdown("### 🔍 Análise de Risco")
        
        risk_insights = []
        
        # Risco LC
        if lc_cur < 1.0:
            deficit = (1.0 - lc_cur) * cur[passivo_circ_col] if passivo_circ_col in df.columns else 0
            risk_insights.append(
                f"🚨 **Risco Alto**: LC {lc_cur:.2f} indica dificuldade para cobrir obrigações de curto prazo"
                + (f" (déficit estimado: R$ {deficit:,.0f})".replace(',', '.') if deficit > 0 else "")
            )
        elif lc_cur < 1.2:
            risk_insights.append(f"⚠️ **Risco Moderado**: LC {lc_cur:.2f} em zona de atenção")
        else:
            risk_insights.append(f"✅ **Risco Baixo**: LC {lc_cur:.2f} adequado para cobertura")
        
        # Tendência
        if delta_lc < -0.1:
            risk_insights.append(f"📉 **Tendência Negativa**: LC caiu {abs(delta_lc):.2f} pontos vs {ano_prev}")
        elif delta_lc > 0.1:
            risk_insights.append(f"📈 **Tendência Positiva**: LC subiu {delta_lc:.2f} pontos vs {ano_prev}")
        
        # LI específico
        if delta_li > 0.1:
            risk_insights.append(f"💰 **Melhora no Caixa**: LI aumentou {delta_li:.2f} (mais liquidez imediata)")
        elif delta_li < -0.1:
            risk_insights.append(f"💸 **Redução do Caixa**: LI caiu {abs(delta_li):.2f} (menos liquidez imediata)")
        
        for insight in risk_insights:
            if "🚨" in insight:
                st.error(insight)
            elif "⚠️" in insight:
                st.warning(insight)
            else:
                st.info(insight)
    
    # -------------------- Endividamento -------------------
    def _render_endividamento_block(self):
        st.subheader("🏦 Estrutura de Endividamento - Análise Completa")
        df = self.analyzer.df.sort_values('Ano')
        required = ['Ano','Passivo Circulante','Passivo Não Circulante']
        if not all(c in df.columns for c in required):
            st.warning("Colunas de passivos ausentes.")
            return
            
        if len(df) < 2:
            st.info("Necessário pelo menos 2 anos para análise comparativa de endividamento.")
            return
            
        prev, cur = df.iloc[-2], df.iloc[-1]
        ano_prev, ano_cur = int(prev['Ano']), int(cur['Ano'])
        
        # ----- Tabela comparativa de passivos -----
        import pandas as pd
        
        pc_prev, pc_cur = prev['Passivo Circulante'], cur['Passivo Circulante']
        pnc_prev, pnc_cur = prev['Passivo Não Circulante'], cur['Passivo Não Circulante']
        total_prev, total_cur = pc_prev + pnc_prev, pc_cur + pnc_cur
        
        passivos_data = [
            {
                'Tipo': 'Curto Prazo',
                f'{ano_prev}': f"R$ {pc_prev:,.0f}".replace(',', '.'),
                f'{ano_cur}': f"R$ {pc_cur:,.0f}".replace(',', '.'),
                'Δ Absoluto': f"R$ {pc_cur - pc_prev:+,.0f}".replace(',', '.'),
                'Δ %': f"{((pc_cur - pc_prev) / pc_prev * 100):+.1f}%" if pc_prev != 0 else "—",
                f'% {ano_prev}': f"{pc_prev / total_prev * 100:.1f}%",
                f'% {ano_cur}': f"{pc_cur / total_cur * 100:.1f}%"
            },
            {
                'Tipo': 'Longo Prazo',
                f'{ano_prev}': f"R$ {pnc_prev:,.0f}".replace(',', '.'),
                f'{ano_cur}': f"R$ {pnc_cur:,.0f}".replace(',', '.'),
                'Δ Absoluto': f"R$ {pnc_cur - pnc_prev:+,.0f}".replace(',', '.'),
                'Δ %': f"{((pnc_cur - pnc_prev) / pnc_prev * 100):+.1f}%" if pnc_prev != 0 else "—",
                f'% {ano_prev}': f"{pnc_prev / total_prev * 100:.1f}%",
                f'% {ano_cur}': f"{pnc_cur / total_cur * 100:.1f}%"
            },
            {
                'Tipo': '📊 TOTAL',
                f'{ano_prev}': f"R$ {total_prev:,.0f}".replace(',', '.'),
                f'{ano_cur}': f"R$ {total_cur:,.0f}".replace(',', '.'),
                'Δ Absoluto': f"R$ {total_cur - total_prev:+,.0f}".replace(',', '.'),
                'Δ %': f"{((total_cur - total_prev) / total_prev * 100):+.1f}%" if total_prev != 0 else "—",
                f'% {ano_prev}': "100.0%",
                f'% {ano_cur}': "100.0%"
            }
        ]
        
        passivos_df = pd.DataFrame(passivos_data)
        st.dataframe(passivos_df, use_container_width=True, hide_index=True)
        
        # ----- Gráficos lado a lado -----
        col1, col2 = st.columns(2)
        
        with col1:
            # Barras comparativas absolutas (melhor que empilhado)
            fig_abs = go.Figure()
            fig_abs.add_bar(
                name='Curto Prazo', 
                x=[str(ano_prev), str(ano_cur)], 
                y=[pc_prev, pc_cur], 
                marker_color='#e74c3c',
                text=[f"R$ {pc_prev:,.0f}".replace(',', '.'), f"R$ {pc_cur:,.0f}".replace(',', '.')],
                textposition='auto'
            )
            fig_abs.add_bar(
                name='Longo Prazo', 
                x=[str(ano_prev), str(ano_cur)], 
                y=[pnc_prev, pnc_cur], 
                marker_color='#3498db',
                text=[f"R$ {pnc_prev:,.0f}".replace(',', '.'), f"R$ {pnc_cur:,.0f}".replace(',', '.')],
                textposition='auto'
            )
            fig_abs.update_layout(
                barmode='stack',
                title='Evolução Absoluta dos Passivos',
                height=400,
                yaxis_title='Valor (R$)',
                yaxis=dict(tickformat=',.0f')
            )
            st.plotly_chart(fig_abs, use_container_width=True)
        
        with col2:
            # Gráfico de composição mais claro
            labels = ['Curto Prazo', 'Longo Prazo']
            values_prev = [pc_prev / total_prev * 100, pnc_prev / total_prev * 100]
            values_cur = [pc_cur / total_cur * 100, pnc_cur / total_cur * 100]
            
            fig_comp = go.Figure()
            # Barras lado a lado em vez de empilhadas
            fig_comp.add_bar(
                name=str(ano_prev), 
                x=labels, 
                y=values_prev, 
                marker_color='#95a5a6',
                text=[f"{v:.1f}%" for v in values_prev],
                textposition='auto'
            )
            fig_comp.add_bar(
                name=str(ano_cur), 
                x=labels, 
                y=values_cur, 
                marker_color='#2c3e50',
                text=[f"{v:.1f}%" for v in values_cur],
                textposition='auto'
            )
            fig_comp.update_layout(
                barmode='group',
                title='Composição % dos Passivos',
                height=400,
                yaxis_title='Participação (%)',
                yaxis=dict(ticksuffix='%', range=[0, 100])
            )
            st.plotly_chart(fig_comp, use_container_width=True)
        
        # ----- Endividamento Geral integrado -----
        if 'Endividamento Geral (EG)' in df.columns:
            eg_prev, eg_cur = prev['Endividamento Geral (EG)'], cur['Endividamento Geral (EG)']
            
            col3, col4 = st.columns([0.7, 0.3])
            with col3:
                # Slope chart do EG
                fig_eg = go.Figure()
                fig_eg.add_trace(go.Scatter(
                    x=[ano_prev, ano_cur], 
                    y=[eg_prev, eg_cur], 
                    mode='lines+markers+text',
                    text=[f"{eg_prev:.1%}", f"{eg_cur:.1%}"],
                    textposition='top center',
                    line=dict(color='#f39c12', width=4),
                    marker=dict(size=12)
                ))
                fig_eg.update_layout(
                    title='Evolução do Endividamento Geral',
                    height=300,
                    yaxis=dict(tickformat='.0%'),
                    showlegend=False
                )
                st.plotly_chart(fig_eg, use_container_width=True)
                
            with col4:
                # Métrica destacada
                delta_eg = eg_cur - eg_prev
                st.metric(
                    "Endividamento Geral", 
                    f"{eg_cur:.1%}",
                    f"{delta_eg:+.1%}"
                )
                
                # Interpretação automática
                if delta_eg > 0.05:  # 5pp
                    st.warning("⚠️ Aumento significativo do endividamento")
                elif delta_eg < -0.05:
                    st.success("✅ Redução significativa do endividamento")
                else:
                    st.info("ℹ️ Endividamento relativamente estável")
        
        # ----- Insights automáticos -----
        st.markdown("### 🔍 Insights Automáticos")
        
        delta_total = total_cur - total_prev
        delta_pc = pc_cur - pc_prev
        delta_pnc = pnc_cur - pnc_prev
        
        insights = []
        
        if abs(delta_total) > total_prev * 0.1:  # Mudança >10%
            direction = "aumentou" if delta_total > 0 else "diminuiu"
            insights.append(f"📈 Endividamento total {direction} R$ {abs(delta_total):,.0f}".replace(',', '.'))
        
        if abs(delta_pc) > abs(delta_pnc):
            maior = "curto prazo" if abs(delta_pc) > abs(delta_pnc) else "longo prazo"
            insights.append(f"🎯 Maior variação foi no {maior}")
        
        # Mudança na composição
        comp_cp_prev = pc_prev / total_prev * 100
        comp_cp_cur = pc_cur / total_cur * 100
        delta_comp = comp_cp_cur - comp_cp_prev
        
        if abs(delta_comp) > 2:  # Mudança >2pp na composição
            direction = "aumentou" if delta_comp > 0 else "diminuiu"
            insights.append(f"⚖️ Participação de curto prazo {direction} {abs(delta_comp):.1f} pontos percentuais")
        
        for insight in insights:
            st.info(insight)
    
    # -------------------- Rentabilidade (DuPont) ----------
    def _render_rentabilidade_block(self):
        st.subheader("📈 Rentabilidade - Análise DuPont Melhorada")
        df = self.analyzer.df.sort_values('Ano')
        required = ['Ano','Margem Líquida (ML)','Giro do Ativo (GA)','Multiplicador de Alavancagem Financeira (MAF)','Rentabilidade do Patrimônio Líquido (ROE) ']
        if not all(c in df.columns for c in required):
            st.warning("Colunas de rentabilidade/duPont ausentes.")
            return
        
        if len(df) < 2:
            st.info("Necessário pelo menos 2 anos para análise DuPont comparativa.")
            return
            
        prev, cur = df.iloc[-2], df.iloc[-1]
        ano_prev, ano_cur = int(prev['Ano']), int(cur['Ano'])
        
        # ----- Waterfall DuPont (substitui o scatter ruim) -----
        ml1, ml2 = prev['Margem Líquida (ML)'], cur['Margem Líquida (ML)']
        ga1, ga2 = prev['Giro do Ativo (GA)'], cur['Giro do Ativo (GA)']
        maf1, maf2 = prev['Multiplicador de Alavancagem Financeira (MAF)'], cur['Multiplicador de Alavancagem Financeira (MAF)']
        roe1, roe2 = prev['Rentabilidade do Patrimônio Líquido (ROE) '], cur['Rentabilidade do Patrimônio Líquido (ROE) ']
        
        import math
        # Aproximação log: dROE_rel ≈ dML/ML + dGA/GA + dMAF/MAF
        def contrib(v1, v2):
            try:
                return math.log(v2/v1) if v1 not in (0, None) and v2 not in (0, None) else 0
            except: 
                return 0
        
        c_ml = contrib(ml1, ml2)
        c_ga = contrib(ga1, ga2)
        c_maf = contrib(maf1, maf2)
        total = (c_ml + c_ga + c_maf) or 1
        
        # Waterfall de contribuição (em pp da variação de ROE)
        delta_roe_pp = (roe2 - roe1) * 100
        
        # Distribui delta_roe_pp proporcional às contribuições percentuais
        values = [
            delta_roe_pp * (c_ml/total), 
            delta_roe_pp * (c_ga/total), 
            delta_roe_pp * (c_maf/total), 
            delta_roe_pp
        ]
        labels = ['Margem', 'Giro', 'MAF', 'Δ ROE (pp)']
        measure = ['relative', 'relative', 'relative', 'total']
        
        wf = go.Figure(go.Waterfall(
            x=labels, 
            measure=measure, 
            y=values, 
            connector={'line': {'color': 'rgba(120,120,120,0.4)'}}
        ))
        wf.update_layout(
            height=420, 
            title=f"Contribuição de cada fator para Δ ROE ({ano_prev} → {ano_cur})"
        )
        st.plotly_chart(wf, use_container_width=True)
        
        # ----- Tabela de detalhes -----
        import pandas as pd
        perc = [("Margem", c_ml/total*100), ("Giro", c_ga/total*100), ("MAF", c_maf/total*100)]
        
        tbl = pd.DataFrame({
            'Fator': ['Margem Líquida', 'Giro do Ativo', 'Multiplicador MAF'],
            f'{ano_prev}': [f"{ml1:.1%}", f"{ga1:.2f}", f"{maf1:.2f}"],
            f'{ano_cur}': [f"{ml2:.1%}", f"{ga2:.2f}", f"{maf2:.2f}"],
            'Δ Absoluto': [f"{ml2-ml1:+.1%}", f"{ga2-ga1:+.2f}", f"{maf2-maf1:+.2f}"],
            'Contrib % Var ROE': [f"{p[1]:+.1f}%" for p in perc]
        })
        st.dataframe(tbl, use_container_width=True, hide_index=True)
        
        # ----- Resumo executivo -----
        maior_contrib = max(perc, key=lambda x: abs(x[1]))
        st.info(f"💡 **Insight**: {maior_contrib[0]} foi o fator que mais impactou o ROE ({maior_contrib[1]:+.1f}% da variação)")
    
    # -------------------- Ciclos / Prazos -----------------
    def _render_ciclos_block(self):
        st.subheader("⏱️ Ciclo Financeiro - Análise Comparativa")
        df = self.analyzer.df.sort_values('Ano')
        required = ['Ano','Prazo Médio de Renovação dos Estoques (PMRE) ','Prazo Médio de Recebimento das Vendas (PMRV) ','Prazo Médio de Pagamento das Compras (PMPC) ','Ciclo Operacional e Ciclo Financeiro']
        if not all(c in df.columns for c in required):
            st.warning("Colunas de ciclo ausentes.")
            return
            
        if len(df) < 2:
            st.info("Necessário pelo menos 2 anos para análise comparativa de ciclos.")
            return
            
        prev, cur = df.iloc[-2], df.iloc[-1]
        ano_prev, ano_cur = int(prev['Ano']), int(cur['Ano'])
        
        # ----- Tabela comparativa dos componentes -----
        import pandas as pd
        componentes = [
            ('PMRE (dias)', 'Prazo Médio de Renovação dos Estoques (PMRE) '),
            ('PMRV (dias)', 'Prazo Médio de Recebimento das Vendas (PMRV) '),
            ('PMPC (dias)', 'Prazo Médio de Pagamento das Compras (PMPC) '),
            ('Ciclo Financeiro', 'Ciclo Operacional e Ciclo Financeiro')
        ]
        
        comp_data = []
        for label, col in componentes:
            val_prev = prev[col]
            val_cur = cur[col]
            delta = val_cur - val_prev
            comp_data.append({
                'Componente': label,
                f'{ano_prev}': f"{val_prev:.0f}",
                f'{ano_cur}': f"{val_cur:.0f}",
                'Δ (dias)': f"{delta:+.0f}",
                'Impacto': '🔺 Aumentou' if delta > 0 else '🔽 Reduziu' if delta < 0 else '➡️ Manteve'
            })
        
        comp_df = pd.DataFrame(comp_data)
        st.dataframe(comp_df, use_container_width=True, hide_index=True)
        
        # ----- Gráfico de barras comparativo -----
        col1, col2 = st.columns(2)
        
        with col1:
            # Barras comparativas dos componentes
            labels = ['PMRE', 'PMRV', 'PMPC']
            valores_prev = [prev[componentes[i][1]] for i in range(3)]
            valores_cur = [cur[componentes[i][1]] for i in range(3)]
            
            fig_comp = go.Figure()
            fig_comp.add_bar(name=str(ano_prev), x=labels, y=valores_prev, marker_color='#bbbbbb')
            fig_comp.add_bar(name=str(ano_cur), x=labels, y=valores_cur, marker_color='#1f77b4')
            fig_comp.update_layout(
                barmode='group', 
                title='Componentes do Ciclo (dias)',
                height=350,
                yaxis_title='Dias'
            )
            st.plotly_chart(fig_comp, use_container_width=True)
        
        with col2:
            # Slope chart do ciclo total
            ciclo_prev = prev['Ciclo Operacional e Ciclo Financeiro']
            ciclo_cur = cur['Ciclo Operacional e Ciclo Financeiro']
            
            fig_slope = go.Figure()
            fig_slope.add_trace(go.Scatter(
                x=[ano_prev, ano_cur], 
                y=[ciclo_prev, ciclo_cur], 
                mode='lines+markers+text',
                text=[f"{ciclo_prev:.0f}", f"{ciclo_cur:.0f}"],
                textposition='top center',
                line=dict(color='#e74c3c', width=4),
                marker=dict(size=12)
            ))
            fig_slope.update_layout(
                title='Evolução do Ciclo Financeiro',
                height=350,
                yaxis_title='Dias',
                showlegend=False
            )
            st.plotly_chart(fig_slope, use_container_width=True)
        
        # ----- Insights automáticos -----
        delta_ciclo = ciclo_cur - ciclo_prev
        if abs(delta_ciclo) >= 2:
            if delta_ciclo > 0:
                st.warning(f"⚠️ **Atenção**: Ciclo financeiro aumentou {delta_ciclo:.0f} dias, indicando maior necessidade de capital de giro")
            else:
                st.success(f"✅ **Positivo**: Ciclo financeiro reduziu {abs(delta_ciclo):.0f} dias, liberando capital de giro")
        else:
            st.info("ℹ️ Ciclo financeiro manteve-se relativamente estável")
        
        # Identificar maior impacto
        deltas = {
            'PMRE': cur[componentes[0][1]] - prev[componentes[0][1]],
            'PMRV': cur[componentes[1][1]] - prev[componentes[1][1]], 
            'PMPC': -(cur[componentes[2][1]] - prev[componentes[2][1]])  # Negativo porque PMPC reduz o ciclo
        }
        maior_impacto = max(deltas.items(), key=lambda x: abs(x[1]))
        
        if abs(maior_impacto[1]) >= 1:
            st.info(f"💡 **Insight**: {maior_impacto[0]} foi o componente que mais impactou o ciclo ({maior_impacto[1]:+.0f} dias)")
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
    # -------------------- MODO SIMPLIFICADO --------------------
    def _render_simplified_overview(self):
        st.subheader("📉 Visão Simplificada (2 anos)")
        df = self.analyzer.df.sort_values('Ano')
        if 'Ano' not in df.columns or len(df['Ano'].unique()) < 2:
            st.info("Necessário pelo menos 2 anos para a visão simplificada.")
            return
        prev, cur = df.iloc[-2], df.iloc[-1]
        ano_prev, ano_cur = int(prev['Ano']), int(cur['Ano'])
        # ----- Slope Charts -----
        st.markdown("### 🔀 Tendência Chave (Slope)")
        metrics_slope = [
            ("ROE", 'Rentabilidade do Patrimônio Líquido (ROE) ', 'pp', 100),
            ("Margem Líquida", 'Margem Líquida (ML)', 'pp', 100),
            ("Giro Ativo", 'Giro do Ativo (GA)', '', 1),
            ("MAF", 'Multiplicador de Alavancagem Financeira (MAF)', '', 1),
            ("Endividamento Geral", 'Endividamento Geral (EG)', '', 1),
            ("Liquidez Corrente", 'Liquidez Corrente (LC) ', '', 1),
        ]
        cols = st.columns(3)
        import plotly.graph_objects as go
        for i,(label,col,kind,scale) in enumerate(metrics_slope):
            with cols[i % 3]:
                if col in df.columns:
                    y_prev = prev[col]
                    y_cur = cur[col]
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=[ano_prev, ano_cur], y=[y_prev, y_cur], mode='lines+markers', line=dict(color='#1f77b4', width=3)))
                    fig.update_layout(height=160, margin=dict(l=10,r=10,t=30,b=10), title=label, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                    delta = (y_cur - y_prev)
                    if kind == 'pp':
                        st.caption(f"Δ {delta*scale:+.1f} pp")
                    else:
                        st.caption(f"Δ {delta:+.2f}")
                else:
                    st.caption(f"{label}: dado ausente")
        st.markdown("---")
        # ----- Delta Bars (Estrutura e Resultado) -----
        st.markdown("### 📊 Variação Estrutural e Resultado")
        estrutura_metrics = [
            ("Ativo Total","Ativo Total"),
            ("Patrimônio Líquido","Patrimônio Líquido"),
            ("Passivo Circulante","Passivo Circulante"),
            ("Passivo Não Circulante","Passivo Não Circulante"),
            ("Receita Líquida","Receita Líquida"),
            ("Lucro Líquido","Lucro Líquido"),
        ]
        bar_data = []
        for label,col in estrutura_metrics:
            if col in df.columns:
                bar_data.append({
                    'Métrica': label,
                    'Anterior': prev[col],
                    'Atual': cur[col],
                    'Delta %': ((cur[col]-prev[col])/prev[col]*100) if prev[col] not in (0,None) else None
                })
        if bar_data:
            import pandas as pd
            delta_df = pd.DataFrame(bar_data)
            # Pequeno gráfico de barras agrupadas
            fig2 = go.Figure()
            fig2.add_bar(x=delta_df['Métrica'], y=delta_df['Anterior'], name=str(ano_prev), marker_color='#bbbbbb')
            fig2.add_bar(x=delta_df['Métrica'], y=delta_df['Atual'], name=str(ano_cur), marker_color='#1f77b4')
            fig2.update_layout(barmode='group', height=420, legend=dict(orientation='h', yanchor='bottom', y=1.02, x=0))
            st.plotly_chart(fig2, use_container_width=True)
            # Tabela de deltas
            show = delta_df.copy()
            show['Δ Abs'] = show['Atual'] - show['Anterior']
            show['Δ %'] = show['Delta %'].map(lambda v: f"{v:+.1f}%" if v is not None else '—')
            st.dataframe(show[['Métrica','Anterior','Atual','Δ Abs','Δ %']], use_container_width=True, hide_index=True)
        else:
            st.info("Sem dados estruturais suficientes.")
        st.markdown("---")
        # ----- Waterfall Lucro -----
        st.markdown("### 💵 Decomposição do Lucro (Waterfall)")
        needed = ['Receita Líquida','Custo dos Produtos Vendidos (CPV)','Lucro Operacional','Lucro Antes dos Impostos','Lucro Líquido']
        if all(c in df.columns for c in needed):
            receita = cur['Receita Líquida']
            cpv = cur['Custo dos Produtos Vendidos (CPV)']
            lucro_bruto = receita - cpv
            lucro_oper = cur['Lucro Operacional']
            despesas_op = -(lucro_oper - lucro_bruto)
            lucro_antes = cur['Lucro Antes dos Impostos']
            resultado_fin = -(lucro_antes - lucro_oper)
            imposto = cur['Lucro Líquido'] - lucro_antes
            waterfall_vals = [receita, -cpv, despesas_op, resultado_fin, imposto, cur['Lucro Líquido']]
            labels = ['Receita','- CPV','Despesas Op.','Resultado Fin./Eq.','Impostos','Lucro Líquido']
            measure = ['relative','relative','relative','relative','relative','total']
            wf = go.Figure(go.Waterfall(x=labels, measure=measure, y=waterfall_vals, connector={'line':{'color':'rgba(100,100,100,0.4)'}}))
            wf.update_layout(height=420, title=f"Waterfall Lucro {ano_cur}")
            st.plotly_chart(wf, use_container_width=True)
        else:
            miss = [c for c in needed if c not in df.columns]
            st.info(f"Waterfall indisponível, faltam colunas: {', '.join(miss)}")
        st.markdown("---")
        # ----- Waterfall DuPont Simplificado -----
        st.markdown("### 🧬 DuPont Simplificado (Contribuição na variação ROE)")
        dup_cols = ['Margem Líquida (ML)','Giro do Ativo (GA)','Multiplicador de Alavancagem Financeira (MAF)','Rentabilidade do Patrimônio Líquido (ROE) ']
        if all(c in df.columns for c in dup_cols):
            ml1,ml2 = prev[dup_cols[0]], cur[dup_cols[0]]
            ga1,ga2 = prev[dup_cols[1]], cur[dup_cols[1]]
            maf1,maf2 = prev[dup_cols[2]], cur[dup_cols[2]]
            roe1,roe2 = prev[dup_cols[3]], cur[dup_cols[3]]
            import math
            # Aproximação log: dROE_rel ≈ dML/ML + dGA/GA + dMAF/MAF
            def contrib(v1,v2):
                try:
                    return math.log(v2/v1) if v1 not in (0,None) and v2 not in (0,None) else 0
                except: return 0
            c_ml = contrib(ml1,ml2)
            c_ga = contrib(ga1,ga2)
            c_maf = contrib(maf1,maf2)
            total = (c_ml + c_ga + c_maf) or 1
            perc = [("Margem", c_ml/total*100), ("Giro", c_ga/total*100), ("MAF", c_maf/total*100)]
            # Waterfall de contribuição (em pp da variação de ROE)
            delta_roe_pp = (roe2 - roe1)*100
            # Distribui delta_roe_pp proporcional às contribuições percentuais
            values = [delta_roe_pp * (c_ml/total), delta_roe_pp * (c_ga/total), delta_roe_pp * (c_maf/total), delta_roe_pp]
            labels = ['Margem','Giro','MAF','Δ ROE (pp)']
            measure = ['relative','relative','relative','total']
            wf2 = go.Figure(go.Waterfall(x=labels, measure=measure, y=values, connector={'line':{'color':'rgba(120,120,120,0.4)'}}))
            wf2.update_layout(height=380, title=f"Contribuição para Δ ROE {ano_prev}->{ano_cur}")
            st.plotly_chart(wf2, use_container_width=True)
            # Tabela
            import pandas as pd
            tbl = pd.DataFrame({
                'Fator':['Margem','Giro','MAF'],
                f'{ano_prev}':[ml1,ga1,maf1],
                f'{ano_cur}':[ml2,ga2,maf2],
                'Δ Abs':[ml2-ml1, ga2-ga1, maf2-maf1],
                'Contrib % Var ROE':[f"{p[1]:+.1f}%" for p in perc]
            })
            st.dataframe(tbl, use_container_width=True, hide_index=True)
        else:
            st.info("DuPont simplificado indisponível (colunas faltando).")
        st.markdown("---")
        # ----- Composição de Capital Simplificada -----
        st.markdown("### 🏦 Estrutura de Capital (Curto vs Longo)")
        cap_cols = ['Passivo Circulante','Passivo Não Circulante']
        if all(c in df.columns for c in cap_cols):
            total_cur = cur['Passivo Circulante'] + cur['Passivo Não Circulante']
            total_prev = prev['Passivo Circulante'] + prev['Passivo Não Circulante']
            comp_fig = go.Figure()
            comp_fig.add_bar(x=[str(ano_prev)], y=[prev['Passivo Circulante']/total_prev*100], name='Curto', marker_color='#ff9999')
            comp_fig.add_bar(x=[str(ano_prev)], y=[prev['Passivo Não Circulante']/total_prev*100], name='Longo', marker_color='#66b3ff')
            comp_fig.add_bar(x=[str(ano_cur)], y=[cur['Passivo Circulante']/total_cur*100], marker_color='#ff9999', showlegend=False)
            comp_fig.add_bar(x=[str(ano_cur)], y=[cur['Passivo Não Circulante']/total_cur*100], marker_color='#66b3ff', showlegend=False)
            comp_fig.update_layout(barmode='stack', height=380, yaxis=dict(ticksuffix='%'), title='Composição % Passivos (Comparação)')
            st.plotly_chart(comp_fig, use_container_width=True)
        else:
            st.info("Composição de capital indisponível.")
        st.caption("Modo simplificado substitui visualizações complexas por deltas claros devido a baixa série temporal.")
