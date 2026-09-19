import streamlit as st
import xml.etree.ElementTree as ET
import pandas as pd
import urllib.parse
import urllib.request
import json

st.set_page_config(page_title="Analisador SAF-T Pro", page_icon="📊", layout="wide")

# Estilo adaptado
st.markdown("""
    <style>
    div[data-testid="stMetric"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        padding: 18px;
        border-radius: 10px;
    }
    div[data-testid="stMetricLabel"] p {
        color: #94a3b8 !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
    }
    div[data-testid="stMetricValue"] div {
        color: #38bdf8 !important;
        font-size: 24px !important;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Painel Executivo SAF-T (PT)")
st.caption("Diagnóstico de faturação, concentração de risco e saúde comercial para empresas portuguesas.")

ficheiro_saft = st.file_uploader("Arraste ou selecione o ficheiro SAF-T (.xml)", type=["xml"])

def corrigir_texto(texto):
    if not texto:
        return ""
    try:
        if "Ã" in texto:
            return texto.encode("latin1").decode("utf-8")
    except Exception:
        pass
    return texto

def processar_saft_bytes(xml_bytes):
    root = ET.fromstring(xml_bytes)
    namespace = {'ns': root.tag.split('}')[0].strip('{')} if '}' in root.tag else {}
    prefix = 'ns:' if namespace else ''

    clientes = {}
    for customer in root.findall(f'.//{prefix}Customer', namespace):
        cust_id = customer.find(f'{prefix}CustomerID', namespace)
        cust_name = customer.find(f'{prefix}CompanyName', namespace)
        if cust_id is not None and cust_name is not None:
            clientes[cust_id.text] = corrigir_texto(cust_name.text)

    dados = []
    for invoice in root.findall(f'.//{prefix}Invoice', namespace):
        doc_no = invoice.find(f'{prefix}InvoiceNo', namespace).text
        doc_type = invoice.find(f'{prefix}InvoiceType', namespace).text
        doc_date = invoice.find(f'{prefix}InvoiceDate', namespace).text
        cust_id = invoice.find(f'{prefix}CustomerID', namespace).text
        
        totais = invoice.find(f'{prefix}DocumentTotals', namespace)
        valor = float(totais.find(f'{prefix}GrossTotal', namespace).text)

        if doc_type == 'NC':
            valor = -valor

        nome_cliente = clientes.get(cust_id, f"Cliente {cust_id}")
        dados.append({
            'Documento': doc_no,
            'Tipo': doc_type,
            'Data': doc_date,
            'Cliente': nome_cliente,
            'Valor': valor
        })

    return pd.DataFrame(dados)

def gerar_html_download(faturacao_liquida, total_faturas, total_nc, maior_cliente_nome, concentracao, top_clientes_df):
    linhas_tabela = ""
    for _, row in top_clientes_df.iterrows():
        linhas_tabela += f"""
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #e2e8f0;">{row['Cliente']}</td>
            <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; text-align: right; font-weight: 600;">{row['Valor (€)']}</td>
            <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; text-align: right; color: #64748b;">{row['% da Receita']}</td>
        </tr>
        """

    return f"""<!DOCTYPE html>
    <html lang="pt">
    <head>
        <meta charset="UTF-8">
        <title>Relatório Executivo Mensal</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8fafc; color: #0f172a; padding: 30px; }}
            .card {{ background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); max-width: 750px; margin: 0 auto; }}
            .kpis {{ display: flex; justify-content: space-between; margin: 20px 0; }}
            .kpi {{ background: #f1f5f9; padding: 15px; border-radius: 6px; width: 30%; text-align: center; }}
            .kpi h4 {{ margin: 0; font-size: 12px; color: #64748b; text-transform: uppercase; }}
            .kpi p {{ margin: 8px 0 0 0; font-size: 20px; font-weight: bold; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 14px; }}
            th {{ background: #f8fafc; padding: 10px; text-align: left; border-bottom: 2px solid #cbd5e1; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Relatório Executivo de Faturação</h2>
            <p style="color: #64748b;">Diagnóstico Automatizado SAF-T</p>
            <div class="kpis">
                <div class="kpi"><h4>Faturação Líquida</h4><p>{faturacao_liquida:,.2f} €</p></div>
                <div class="kpi"><h4>Total Documentos</h4><p>{total_faturas} (NC: {total_nc})</p></div>
                <div class="kpi"><h4>Risco Cliente Top</h4><p>{concentracao:.1f}%</p></div>
            </div>
            <h3>Detetor de Receita por Cliente</h3>
            <table>
                <thead>
                    <tr><th>Cliente</th><th style="text-align: right;">Total (€)</th><th style="text-align: right;">% Receita</th></tr>
                </thead>
                <tbody>{linhas_tabela}</tbody>
            </table>
        </div>
    </body>
    </html>"""

if ficheiro_saft is not None:
    try:
        bytes_data = ficheiro_saft.read()
        df = processar_saft_bytes(bytes_data)

        faturacao_liquida = df['Valor'].sum()
        faturas_positivas = df[df['Tipo'] != 'NC']
        total_faturas = len(faturas_positivas)
        total_nc = len(df[df['Tipo'] == 'NC'])
        ticket_medio = faturacao_liquida / total_faturas if total_faturas > 0 else 0
        
        df_clientes = df.groupby('Cliente')['Valor'].sum().sort_values(ascending=False).reset_index()
        df_clientes['% da Receita'] = (df_clientes['Valor'] / faturacao_liquida * 100).map("{:.1f}%".format)
        df_clientes['Valor (€)'] = df_clientes['Valor'].map("{:,.2f} €".format)

        maior_cliente_nome = df_clientes.iloc[0]['Cliente']
        maior_cliente_valor = df.groupby('Cliente')['Valor'].sum().max()
        concentracao = (maior_cliente_valor / faturacao_liquida) * 100 if faturacao_liquida > 0 else 0

        st.divider()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Faturação Líquida", f"{faturacao_liquida:,.2f} €")
        col2.metric("Ticket Médio", f"{ticket_medio:,.2f} €")
        col3.metric("Faturas Emitidas", f"{total_faturas}", f"NCs: {total_nc}", delta_color="inverse")
        col4.metric("Risco de Concentração", f"{concentracao:.1f}%")

        if concentracao > 40:
            st.warning(f"⚠️ **Alerta de Dependência:** O cliente **{maior_cliente_nome}** representa **{concentracao:.1f}%** da receita. Risco elevado para o fluxo de tesouraria.")

        col_grafico, col_tabela = st.columns([1.2, 1])

        with col_grafico:
            st.subheader("Top Clientes por Faturação")
            grafico_data = df.groupby('Cliente')['Valor'].sum().sort_values(ascending=True)
            st.bar_chart(grafico_data, horizontal=True)

        with col_tabela:
            st.subheader("Detetor de Receita")
            st.dataframe(
                df_clientes[['Cliente', 'Valor (€)', '% da Receita']], 
                use_container_width=True, 
                hide_index=True
            )

        st.divider()
        html_doc = gerar_html_download(faturacao_liquida, total_faturas, total_nc, maior_cliente_nome, concentracao, df_clientes)
        
        st.download_button(
            label="📄 Descarregar Relatório Executivo (HTML/PDF)",
            data=html_doc,
            file_name="relatorio_executivo.html",
            mime="text/html"
        )

        # ---------------- SEÇÃO DE CAPTURA DE LEADS E CONVERSÃO ----------------
        st.markdown("---")
        st.subheader("💼 Quer receber este acompanhamento todos os meses?")
        st.write("Disponibilizamos planos mensais para **empresas** e versões personalizadas com logótipo para **gabinetes de contabilidade**.")

        col_form, col_whats = st.columns([1.2, 1])

        MEU_EMAIL_NOTIFICACAO = "gestao.saft.pt@gmail.com"

        with col_form:
            with st.form("form_contacto"):
                st.markdown("**Pedir contacto ou proposta:**")
                nome = st.text_input("O seu Nome")
                contacto = st.text_input("E-mail ou Telemóvel")
                tipo_perfil = st.selectbox("Perfil:", ["Empresa / Gestor", "Gabinete de Contabilidade"])
                submetido = st.form_submit_button("Pedir Acesso ao Plano Mensal")

                if submetido:
                    if nome and contacto:
                        try:
                            payload = json.dumps({
                                "nome": nome,
                                "contacto": contacto,
                                "perfil": tipo_perfil,
                                "_subject": f"🔥 Novo Lead SAF-T: {nome}",
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
                            st.error(f"Erro no envio: {e}")
                    else:
                        st.error("Por favor, preencha o seu nome e contacto.")

        with col_whats:
            st.markdown("**Prefere falar diretamente por WhatsApp?**")
            st.write("Tire dúvidas instantâneas ou solicite um teste para a sua carteira de clientes:")
            
            numero_whatsapp = "351935009099" 
            mensagem_padrao = "Olá! Estive a testar o Analisador SAF-T Pro e gostaria de saber mais informações sobre os planos mensais."
            url_whatsapp = f"https://wa.me/{numero_whatsapp}?text={urllib.parse.quote(mensagem_padrao)}"
            
            st.link_button("💬 Conversar no WhatsApp", url_whatsapp, type="primary")

    except Exception as e:
        st.error(f"Erro ao processar ficheiro: {e}")
else:
    st.info("Aguardando upload de um ficheiro SAF-T de faturação...")
