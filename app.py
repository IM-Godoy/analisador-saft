import streamlit as st
import xml.etree.ElementTree as ET
import pandas as pd
import urllib.parse
import urllib.request
import json

st.set_page_config(
    page_title="SAF-T Intelligence Pro | Gestão Executiva", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- ESTILOS VISUAIS PREMIUM (DARK SAAS) ----------------
st.markdown("""
    <style>
    /* Estilo Geral de Cabeçalho */
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 26px;
        margin-bottom: 25px;
    }
    .badge-pill {
        display: inline-block;
        padding: 4px 12px;
        font-size: 11px;
        font-weight: 700;
        border-radius: 9999px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }
    .badge-blue { background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); }
    .badge-green { background: rgba(34, 197, 94, 0.15); color: #22c55e; border: 1px solid rgba(34, 197, 94, 0.3); }
    .badge-amber { background: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3); }
    .badge-purple { background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3); }

    /* Cartões de Métricas */
    div[data-testid="stMetric"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        padding: 16px;
        border-radius: 12px;
    }
    div[data-testid="stMetricLabel"] p {
        color: #94a3b8 !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
    }
    div[data-testid="stMetricValue"] div {
        color: #f8fafc !important;
        font-size: 22px !important;
        font-weight: 700;
    }

    /* Cartões de Funcionalidade da Hero */
    .hero-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 22px;
        height: 100%;
    }

    /* Cartões de Preço / Pricing Cards */
    .pricing-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 26px 22px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .pricing-card-featured {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border: 2px solid #38bdf8;
        box-shadow: 0 8px 24px rgba(56, 189, 248, 0.15);
        border-radius: 14px;
        padding: 26px 22px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .pricing-price {
        font-size: 32px;
        font-weight: 800;
        color: #f8fafc;
        margin: 12px 0 4px 0;
    }
    .pricing-sub {
        font-size: 13px;
        color: #94a3b8;
        margin-bottom: 20px;
    }
    .feature-list {
        list-style: none;
        padding: 0;
        margin: 0 0 24px 0;
        font-size: 14px;
        color: #cbd5e1;
    }
    .feature-list li {
        margin-bottom: 10px;
        display: flex;
        align-items: center;
    }
    .check-icon {
        color: #22c55e;
        font-weight: bold;
        margin-right: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------- MOTOR DE PROCESSAMENTO SAF-T ----------------
def corrigir_texto(texto):
    if not texto:
        return ""
    try:
        if "Ã" in texto:
            return texto.encode("latin1").decode("utf-8")
    except Exception:
        pass
    return texto

def processar_saft_completo(xml_bytes):
    root = ET.fromstring(xml_bytes)
    namespace = {'ns': root.tag.split('}')[0].strip('{')} if '}' in root.tag else {}
    prefix = 'ns:' if namespace else ''

    clientes = {}
    for customer in root.findall(f'.//{prefix}Customer', namespace):
        cust_id = customer.find(f'{prefix}CustomerID', namespace)
        cust_name = customer.find(f'{prefix}CompanyName', namespace)
        if cust_id is not None and cust_name is not None:
            clientes[cust_id.text] = corrigir_texto(cust_name.text)

    dados_faturas = []
    dados_iva = []

    for invoice in root.findall(f'.//{prefix}Invoice', namespace):
        doc_no = invoice.find(f'{prefix}InvoiceNo', namespace).text
        doc_type = invoice.find(f'{prefix}InvoiceType', namespace).text
        doc_date = invoice.find(f'{prefix}InvoiceDate', namespace).text
        cust_id = invoice.find(f'{prefix}CustomerID', namespace).text
        
        totais = invoice.find(f'{prefix}DocumentTotals', namespace)
        valor_bruto = float(totais.find(f'{prefix}GrossTotal', namespace).text)
        valor_liquido = float(totais.find(f'{prefix}NetTotal', namespace).text) if totais.find(f'{prefix}NetTotal', namespace) is not None else valor_bruto
        imposto_doc = float(totais.find(f'{prefix}TaxPayable', namespace).text) if totais.find(f'{prefix}TaxPayable', namespace) is not None else 0.0

        if doc_type == 'NC':
            valor_bruto = -abs(valor_bruto)
            valor_liquido = -abs(valor_liquido)
            imposto_doc = -abs(imposto_doc)

        dados_faturas.append({
            'Documento': doc_no,
            'Tipo': doc_type,
            'Data': doc_date,
            'Cliente': clientes.get(cust_id, f"Cliente {cust_id}"),
            'ValorBruto': valor_bruto,
            'ValorLiquido': valor_liquido,
            'Imposto': imposto_doc
        })

        for line in invoice.findall(f'.//{prefix}Line', namespace):
            tax_elem = line.find(f'{prefix}Tax', namespace)
            if tax_elem is not None:
                t_code = tax_elem.find(f'{prefix}TaxCode', namespace)
                t_perc = tax_elem.find(f'{prefix}TaxPercentage', namespace)
                t_amt = tax_elem.find(f'{prefix}TaxAmount', namespace)
                
                tax_rate = float(t_perc.text) if t_perc is not None and t_perc.text else 0.0
                tax_code = t_code.text if t_code is not None and t_code.text else "OUT"
                
                credit = line.find(f'{prefix}CreditAmount', namespace)
                debit = line.find(f'{prefix}DebitAmount', namespace)
                base = float(credit.text) if credit is not None and credit.text else (float(debit.text) if debit is not None and debit.text else 0.0)
                
                if doc_type == 'NC':
                    base = -abs(base)
                
                tax_val = float(t_amt.text) if t_amt is not None and t_amt.text else base * (tax_rate / 100.0)
                if doc_type == 'NC':
                    tax_val = -abs(tax_val)

                dados_iva.append({
                    'TaxCode': tax_code,
                    'TaxRate': tax_rate,
                    'Base': base,
                    'ValorIVA': tax_val
                })

    return pd.DataFrame(dados_faturas), pd.DataFrame(dados_iva)

# ---------------- FUNÇÃO PARA EXIBIR A TABELA DE PREÇOS MODERNA ----------------
def exibir_tabela_precos():
    st.markdown("### 💎 Planos & Preços Transparentes")
    st.markdown("Escolha a opção ideal para a sua empresa ou para a carteira de clientes do seu gabinete de contabilidade.")
    
    col_p1, col_p2, col_p3 = st.columns(3)

    # Plano 1: Grátis
    with col_p1:
        st.markdown("""
        <div class="pricing-card">
            <div>
                <span class="badge-pill badge-blue">Para Testes</span>
                <h3 style="margin: 0; color: #f8fafc;">Diagnóstico Pontual</h3>
                <div class="pricing-price">0 €</div>
                <div class="pricing-sub">Gratuito para sempre</div>
                <ul class="feature-list">
                    <li><span class="check-icon">✓</span> Leitura instantânea de 1 SAF-T</li>
                    <li><span class="check-icon">✓</span> KPIs de Faturação Líquida e Ticket Médio</li>
                    <li><span class="check-icon">✓</span> Detetor básico de Concentração Top 1</li>
                    <li><span class="check-icon">✓</span> Relatório executivo básico em ecrã</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.button("Plano Atual (Carregue SAF-T)", disabled=True, key="btn_free")

    # Plano 2: PME Gestão
    with col_p2:
        st.markdown("""
        <div class="pricing-card">
            <div>
                <span class="badge-pill badge-green">Para Empresas</span>
                <h3 style="margin: 0; color: #f8fafc;">PME Gestão</h3>
                <div class="pricing-price">29 € <span style="font-size: 15px; color: #94a3b8; font-weight: normal;">/mês</span></div>
                <div class="pricing-sub">Acompanhamento contínuo da empresa</div>
                <ul class="feature-list">
                    <li><span class="check-icon">✓</span> <b>Tudo do plano gratuito</b></li>
                    <li><span class="check-icon">✓</span> Análise Mensal Automatizada por E-mail</li>
                    <li><span class="check-icon">✓</span> <b>Relatório Homólogo</b> (Mês vs Mês Anterior)</li>
                    <li><span class="check-icon">✓</span> Detetor de Perda de Clientes (Churn)</li>
                    <li><span class="check-icon">✓</span> Alertas de Risco de Tesouraria no WhatsApp</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        msg_pme = "Olá! Gostaria de subscrever o Plano PME Gestão (29€/mês) para a minha empresa."
        url_pme = f"https://wa.me/351935009099?text={urllib.parse.quote(msg_pme)}"
        st.link_button("🚀 Subscrever Plano PME (29€)", url_pme, use_container_width=True)

    # Plano 3: Gabinete Pro (Destaque)
    with col_p3:
        st.markdown("""
        <div class="pricing-card-featured">
            <div>
                <span class="badge-pill badge-purple">⭐ Mais Escolhido</span>
                <h3 style="margin: 0; color: #f8fafc;">Gabinete Pro</h3>
                <div class="pricing-price">79 € <span style="font-size: 15px; color: #38bdf8; font-weight: normal;">/mês</span></div>
                <div class="pricing-sub">Para Gabinetes de Contabilidade & TOCs</div>
                <ul class="feature-list">
                    <li><span class="check-icon">✓</span> <b>Até 30 empresas da carteira</b> incluídas</li>
                    <li><span class="check-icon">✓</span> <b>White-Label:</b> Relatórios com o logótipo do gabinete</li>
                    <li><span class="check-icon">✓</span> Mapa de Auditoria de IVA para apoio fiscal</li>
                    <li><span class="check-icon">✓</span> Exportação executiva em 1 clique para enviar aos clientes</li>
                    <li><span class="check-icon">✓</span> Suporte prioritário dedicado por WhatsApp</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        msg_gab = "Olá! Gostaria de ativar o Plano Gabinete Pro (79€/mês) para a carteira de clientes do meu gabinete."
        url_gab = f"https://wa.me/351935009099?text={urllib.parse.quote(msg_gab)}"
        st.link_button("⭐ Aderir ao Gabinete Pro (79€)", url_gab, type="primary", use_container_width=True)

# ---------------- CABEÇALHO PRINCIPAL ----------------
st.markdown("""
<div class="main-header">
    <span class="badge-pill badge-blue">SAF-T Executive Analytics v2.5</span>
    <h1 style="margin: 0; font-size: 28px; color: #f8fafc;">⚡ Plataforma de Inteligência e Auditoria SAF-T</h1>
    <p style="margin: 6px 0 0 0; color: #94a3b8; font-size: 15px;">
        Transforme ficheiros fiscais mensais num diagnóstico executivo de faturação, dependência de clientes e IVA.
    </p>
</div>
""", unsafe_allow_html=True)

ficheiro_saft = st.file_uploader("📂 Arraste ou selecione o ficheiro SAF-T (.xml) da empresa", type=["xml"])

# ---------------- CASO 1: PÁGINA INICIAL (ANTES DO UPLOAD) ----------------
if ficheiro_saft is None:
    st.markdown("### Porquê analisar o SAF-T com a nossa plataforma?")
    col_h1, col_h2, col_h3 = st.columns(3)

    with col_h1:
        st.markdown("""
        <div class="hero-card">
            <span class="badge-pill badge-green">Segurança Máxima</span>
            <h3 style="margin-top: 5px; color: #f8fafc;">🔒 100% Confidencial</h3>
            <p style="color: #94a3b8; font-size: 14px;">
                Os ficheiros são processados na memória volátil do navegador. Nenhum dado financeiro ou fiscal é armazenado em bases de dados externas.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_h2:
        st.markdown("""
        <div class="hero-card">
            <span class="badge-pill badge-blue">Gestão Estratégica</span>
            <h3 style="margin-top: 5px; color: #f8fafc;">📊 Curva ABC & Risco 80/20</h3>
            <p style="color: #94a3b8; font-size: 14px;">
                Descubra instantaneamente quais os clientes críticos que asseguram 80% do fluxo de caixa e identifique a concentração de risco comercial.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_h3:
        st.markdown("""
        <div class="hero-card">
            <span class="badge-pill badge-amber">Conferência Fiscal</span>
            <h3 style="margin-top: 5px; color: #f8fafc;">⚖️ Auditoria de IVA</h3>
            <p style="color: #94a3b8; font-size: 14px;">
                Resumo instantâneo de faturas emitidas vs. notas de crédito, com desdobramento por taxas normal (23%), intermédia, reduzida e isenções.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    # TABELA DE PREÇOS NA HOME PAGE
    exibir_tabela_precos()

# ---------------- CASO 2: FICHEIRO CARREGADO COM SUCESSO ----------------
else:
    try:
        bytes_data = ficheiro_saft.read()
        df, df_tax = processar_saft_completo(bytes_data)

        # Cálculos Globais
        faturas_positivas = df[df['Tipo'] != 'NC']
        notas_credito = df[df['Tipo'] == 'NC']

        fat_bruta = faturas_positivas['ValorBruto'].sum()
        total_nc = abs(notas_credito['ValorBruto'].sum())
        fat_liquida = df['ValorBruto'].sum()
        total_iva = df['Imposto'].sum()

        taxa_nc = (total_nc / fat_bruta * 100) if fat_bruta > 0 else 0
        total_docs = len(faturas_positivas)
        ticket_medio = fat_liquida / total_docs if total_docs > 0 else 0

        # Análise de Concentração
        df_clientes = df.groupby('Cliente')['ValorBruto'].sum().sort_values(ascending=False).reset_index()
        top_cliente_nome = df_clientes.iloc[0]['Cliente'] if not df_clientes.empty else "N/D"
        top_cliente_val = df_clientes.iloc[0]['ValorBruto'] if not df_clientes.empty else 0
        concentracao_top1 = (top_cliente_val / fat_liquida * 100) if fat_liquida > 0 else 0

        # NAVEGAÇÃO POR TABS
        tab_visao, tab_abc, tab_iva, tab_plano = st.tabs([
            "📈 Visão Geral Executiva",
            "👥 Curva ABC & Concentração",
            "⚖️ Auditoria de IVA & Fiscal",
            "💎 Planos & Relatório"
        ])

        # ---------------- TAB 1: VISÃO GERAL ----------------
        with tab_visao:
            st.markdown("#### Indicadores Principais de Saúde Comercial")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Faturação Líquida", f"{fat_liquida:,.2f} €")
            c2.metric("Ticket Médio Real", f"{ticket_medio:,.2f} €")
            c3.metric("Faturas Emitidas", f"{total_docs}", f"{len(notas_credito)} NCs anuladas", delta_color="inverse")
            c4.metric("Risco Concentração Top 1", f"{concentracao_top1:.1f}%")

            c5, c6, c7, c8 = st.columns(4)
            c5.metric("Volume Bruto Total", f"{fat_bruta:,.2f} €")
            c6.metric("Total Devoluções (NC)", f"{total_nc:,.2f} €")
            c7.metric("Taxa de Devoluções (% NC)", f"{taxa_nc:.2f}%")
            c8.metric("Total IVA Liquidado", f"{total_iva:,.2f} €")

            st.markdown("---")
            st.markdown("#### Diagnóstico Rápido de Risco")
            d_col1, d_col2 = st.columns(2)
            with d_col1:
                if concentracao_top1 > 40:
                    st.error(f"🚨 **Dependência Crítica de Carteira:** O cliente **{top_cliente_nome}** gera **{concentracao_top1:.1f}%** de toda a receita. A perda deste cliente compromete a estrutura de custos.")
                elif concentracao_top1 > 25:
                    st.warning(f"⚠️ **Atenção à Concentração:** O principal cliente representa **{concentracao_top1:.1f}%** do volume de negócios.")
                else:
                    st.success(f"✅ **Carteira Saudável:** A receita está bem distribuída. O cliente líder pesa apenas **{concentracao_top1:.1f}%**.")

            with d_col2:
                if taxa_nc > 5:
                    st.error(f"🚨 **Taxa de Anulação Alta ({taxa_nc:.1f}%):** O valor devolvido em notas de crédito supera os padrões saudáveis (>5%). Indicador de possíveis falhas na operação ou faturação errática.")
                else:
                    st.success(f"✅ **Operação Eficiente:** Taxa de notas de crédito reduzida ({taxa_nc:.1f}%), dentro dos parâmetros de excelência.")

            st.markdown("---")
            st.markdown("#### Ritmo Diário de Vendas no Período")
            df['Data_dt'] = pd.to_datetime(df['Data'], errors='coerce')
            df_diario = df.groupby(df['Data_dt'].dt.date)['ValorBruto'].sum().reset_index()
            df_diario.columns = ['Data', 'Faturação Diária (€)']
            st.line_chart(df_diario.set_index('Data'), color="#38bdf8")

        # ---------------- TAB 2: CURVA ABC (PARETO) ----------------
        with tab_abc:
            st.markdown("#### Classificação de Clientes por Importância Estratégica (Regra 80/20)")
            st.caption("Segmentação automática dos clientes que sustentam o volume financeiro da empresa.")

            df_abc = df_clientes[df_clientes['ValorBruto'] > 0].copy()
            total_rev_abc = df_abc['ValorBruto'].sum()
            df_abc['% Receita'] = (df_abc['ValorBruto'] / total_rev_abc) * 100
            df_abc['% Acumulada'] = df_abc['% Receita'].cumsum()

            def classificar_pareto(perc_acum):
                if perc_acum <= 80.0:
                    return "Classe A (Crítico - 80%)"
                elif perc_acum <= 95.0:
                    return "Classe B (Estratégico - 15%)"
                else:
                    return "Classe C (Cauda Longa - 5%)"

            df_abc['Categoria ABC'] = df_abc['% Acumulada'].apply(classificar_pareto)

            total_a = len(df_abc[df_abc['Categoria ABC'].str.contains('Classe A')])
            total_b = len(df_abc[df_abc['Categoria ABC'].str.contains('Classe B')])
            total_c = len(df_abc[df_abc['Categoria ABC'].str.contains('Classe C')])

            abc1, abc2, abc3 = st.columns(3)
            abc1.metric("Clientes Classe A (80% da Receita)", f"{total_a} clientes", "Impacto Máximo", delta_color="normal")
            abc2.metric("Clientes Classe B (15% da Receita)", f"{total_b} clientes", "Potencial de Crescimento", delta_color="off")
            abc3.metric("Clientes Classe C (5% da Receita)", f"{total_c} clientes", "Alto Custo Operacional", delta_color="inverse")

            col_abc_chart, col_abc_table = st.columns([1.2, 1])
            with col_abc_chart:
                st.subheader("Top Clientes da Carteira")
                st.bar_chart(df_abc.head(10).set_index('Cliente')['ValorBruto'], horizontal=True, color="#38bdf8")

            with col_abc_table:
                st.subheader("Detetor Estratégico")
                df_exibicao = df_abc[['Cliente', 'ValorBruto', '% Receita', 'Categoria ABC']].copy()
                df_exibicao['ValorBruto'] = df_exibicao['ValorBruto'].map("{:,.2f} €".format)
                df_exibicao['% Receita'] = df_exibicao['% Receita'].map("{:.2f}%".format)
                st.dataframe(df_exibicao, use_container_width=True, hide_index=True)

        # ---------------- TAB 3: AUDITORIA FISCAL & IVA ----------------
        with tab_iva:
            st.markdown("#### Resumo Fiscal de IVA Liquidado")
            st.caption("Conferência automática por escalão tributável para gabinetes de contabilidade e TOCs.")

            if not df_tax.empty:
                df_tax_resumo = df_tax.groupby(['TaxCode', 'TaxRate'])[['Base', 'ValorIVA']].sum().reset_index()
                df_tax_resumo.columns = ['Código', 'Taxa (%)', 'Base Tributável (€)', 'IVA Liquidado (€)']
                
                iva_col1, iva_col2 = st.columns(2)
                iva_col1.metric("Total da Base Tributável", f"{df_tax_resumo['Base Tributável (€)'].sum():,.2f} €")
                iva_col2.metric("Total IVA Declarado", f"{df_tax_resumo['IVA Liquidado (€)'].sum():,.2f} €")

                st.markdown("##### Repartição por Taxa:")
                df_tax_show = df_tax_resumo.copy()
                df_tax_show['Taxa (%)'] = df_tax_show['Taxa (%)'].map("{:.1f}%".format)
                df_tax_show['Base Tributável (€)'] = df_tax_show['Base Tributável (€)'].map("{:,.2f} €".format)
                df_tax_show['IVA Liquidado (€)'] = df_tax_show['IVA Liquidado (€)'].map("{:,.2f} €".format)
                st.dataframe(df_tax_show, use_container_width=True, hide_index=True)
            else:
                st.info("O ficheiro SAF-T carregado não possui detalhe granular por linha de imposto. O total apurado no documento foi de: " + f"{total_iva:,.2f} €")

        # ---------------- TAB 4: PLANOS & RELATÓRIO ----------------
        with tab_plano:
            st.markdown("#### 📄 Relatório Executivo do SAF-T Carregado")
            
            html_linhas = ""
            for _, row in df_clientes.head(15).iterrows():
                p_cli = (row['ValorBruto'] / fat_liquida * 100) if fat_liquida > 0 else 0
                html_linhas += f"""
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">{row['Cliente']}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; text-align: right; font-weight: 600;">{row['ValorBruto']:,.2f} €</td>
                    <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; text-align: right;">{p_cli:.1f}%</td>
                </tr>
                """

            html_doc = f"""<!DOCTYPE html>
            <html lang="pt">
            <head>
                <meta charset="UTF-8">
                <title>Relatório Executivo Mensal</title>
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8fafc; color: #0f172a; padding: 30px; }}
                    .card {{ background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); max-width: 800px; margin: 0 auto; }}
                    .kpis {{ display: flex; justify-content: space-between; margin: 20px 0; }}
                    .kpi {{ background: #f1f5f9; padding: 15px; border-radius: 6px; width: 30%; text-align: center; }}
                    .kpi h4 {{ margin: 0; font-size: 11px; color: #64748b; text-transform: uppercase; }}
                    .kpi p {{ margin: 8px 0 0 0; font-size: 18px; font-weight: bold; }}
                    table {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 13px; }}
                    th {{ background: #f8fafc; padding: 8px; text-align: left; border-bottom: 2px solid #cbd5e1; }}
                </style>
            </head>
            <body>
                <div class="card">
                    <h2>Relatório Executivo de Gestão & Faturação</h2>
                    <p style="color: #64748b; font-size: 13px;">Auditoria Automatizada via SAF-T</p>
                    <div class="kpis">
                        <div class="kpi"><h4>Faturação Líquida</h4><p>{fat_liquida:,.2f} €</p></div>
                        <div class="kpi"><h4>Ticket Médio</h4><p>{ticket_medio:,.2f} €</p></div>
                        <div class="kpi"><h4>Risco Cliente Top</h4><p>{concentracao_top1:.1f}%</p></div>
                    </div>
                    <h3>Top 15 Clientes da Carteira</h3>
                    <table>
                        <thead>
                            <tr><th>Cliente</th><th style="text-align: right;">Total (€)</th><th style="text-align: right;">% Receita</th></tr>
                        </thead>
                        <tbody>{html_linhas}</tbody>
                    </table>
                </div>
            </body>
            </html>"""

            st.download_button(
                label="📥 Descarregar Relatório Executivo (HTML/PDF)",
                data=html_doc,
                file_name="relatorio_saft_executivo.html",
                mime="text/html"
            )

            st.markdown("---")
            # TABELA DE PREÇOS DENTRO DO SEPARADOR
            exibir_tabela_precos()

            st.markdown("---")
            st.subheader("📬 Fale Connosco ou Peça uma Demonstração Personalizada")
            
            col_form, col_whats = st.columns([1.2, 1])
            MEU_EMAIL_NOTIFICACAO = "gestao.saft.pt@gmail.com"

            with col_form:
                with st.form("form_contacto_v2"):
                    st.markdown("**Pedir contacto ou proposta por e-mail:**")
                    nome = st.text_input("O seu Nome")
                    contacto = st.text_input("E-mail ou Telemóvel")
                    tipo_perfil = st.selectbox("Plano de Interesse:", ["Plano PME Gestão (29 €/mês)", "Plano Gabinete Pro (79 €/mês)", "Demonstração para Gabinete"])
                    submetido = st.form_submit_button("Pedir Informações")

                    if submetido:
                        if nome and contacto:
                            try:
                                payload = json.dumps({
                                    "nome": nome,
                                    "contacto": contacto,
                                    "perfil": tipo_perfil,
                                    "_subject": f"🔥 Novo Lead SAF-T Pro: {nome}",
                                    "_captcha": "false"
                                }).encode("utf-8")

                                req = urllib.request.Request(
                                    f"https://formsubmit.co/ajax/{MEU_EMAIL_NOTIFICACAO}",
                                    data=payload,
                                    headers={
                                        "Content-Type": "application/json",
                                        "Accept": "application/json",
                                        "User-Agent": "Mozilla/5.0",
                                        "Referer": "https://im-godoy-analisador-saft-app-xwvmax.streamlit.app"
                                    }
                                )

                                with urllib.request.urlopen(req) as resp:
                                    res_json = json.loads(resp.read().decode("utf-8"))
                                    if str(res_json.get("success")).lower() == "true":
                                        st.success("✅ Pedido registado com sucesso! Entraremos em contacto em até 24 horas.")
                                    elif "message" in res_json:
                                        st.info(f"ℹ️ {res_json['message']}")
                                    else:
                                        st.success("✅ Pedido registado com sucesso!")
                            except Exception as e:
                                st.error(f"Erro ao submeter: {e}")
                        else:
                            st.error("Por favor, preencha o seu nome e contacto.")

            with col_whats:
                st.markdown("**Contacto Imediato por WhatsApp:**")
                st.write("Fale diretamente connosco para tirar dúvidas ou solicitar integração para a sua carteira:")
                
                numero_whatsapp = "351935009099" 
                msg_whats_geral = "Olá! Estive a testar a plataforma SAF-T Intelligence Pro e gostaria de tirar algumas dúvidas sobre os planos."
                url_whatsapp = f"https://wa.me/{numero_whatsapp}?text={urllib.parse.quote(msg_whats_geral)}"
                
                st.link_button("💬 Abrir Conversa no WhatsApp", url_whatsapp, type="primary", use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao processar ficheiro SAF-T: {e}")
