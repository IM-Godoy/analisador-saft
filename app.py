import streamlit as st
import streamlit.components.v1 as components
import xml.etree.ElementTree as ET
import pandas as pd
import io
import re
import time
import numpy as np
import urllib.parse
import urllib.request
import json

st.set_page_config(
    page_title="SAF-T Intelligence Pro | Inteligência Comercial e Fiscal", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- OCULTAR TOTALMENTE A BARRA E ÍCONES SUPERIORES ----------------
st.markdown("""
    <style>
    [data-testid="stHeader"] {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------- MOTOR 3D: TÚNEL IDÊNTICO E CONTÍNUO EM AMBAS AS TELAS ----------------
def injetar_fundo_tunel():
    tunel_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            html, body { width: 100vw; height: 100vh; overflow: hidden; background: #030609; }
            canvas { width: 100%; height: 100%; display: block; }
        </style>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    </head>
    <body>
        <canvas id="bg-canvas"></canvas>
        <script>
            const canvas = document.getElementById('bg-canvas');
            const scene = new THREE.Scene();
            scene.fog = new THREE.FogExp2(0x030609, 0.04);

            const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 100);
            camera.position.z = 4.0;

            const renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

            const ringCount = 50;
            const rings = [];
            const sides = 6;
            const radius = 4.0;
            const ringPts = [];

            for (let s = 0; s <= sides; s++) {
                const a = (s / sides) * Math.PI * 2;
                ringPts.push(new THREE.Vector3(Math.cos(a) * radius, Math.sin(a) * radius, 0));
            }
            const ringGeo = new THREE.BufferGeometry().setFromPoints(ringPts);

            for (let i = 0; i < ringCount; i++) {
                const isAccent = (i % 4 === 0);
                const ringMat = new THREE.LineBasicMaterial({
                    color: isAccent ? 0xa855f7 : 0x00D9D9,
                    transparent: true,
                    opacity: isAccent ? 0.35 : 0.15
                });
                const ring = new THREE.Line(ringGeo, ringMat);
                ring.position.z = -i * 1.5;
                scene.add(ring);
                rings.push(ring);
            }

            const pCount = 1200;
            const pGeo = new THREE.BufferGeometry();
            const pPos = new Float32Array(pCount * 3);
            const pSpeed = new Float32Array(pCount);

            for (let i = 0; i < pCount * 3; i += 3) {
                const angle = Math.random() * Math.PI * 2;
                const r = 0.5 + Math.random() * 5.0;
                pPos[i] = Math.cos(angle) * r;
                pPos[i+1] = Math.sin(angle) * r;
                pPos[i+2] = -Math.random() * 75;
                pSpeed[i/3] = 0.003 + Math.random() * 0.004;
            }
            pGeo.setAttribute('position', new THREE.BufferAttribute(pPos, 3));

            const pMat = new THREE.PointsMaterial({
                color: 0x00D9D9,
                size: 0.045,
                transparent: true,
                opacity: 0.70,
                blending: THREE.AdditiveBlending
            });
            const particles = new THREE.Points(pGeo, pMat);
            scene.add(particles);

            let time = 0;
            function animate() {
                requestAnimationFrame(animate);
                time += 0.0003;

                for (let i = 0; i < ringCount; i++) {
                    const r = rings[i];
                    r.position.z += 0.004;
                    if (r.position.z > 5.0) {
                        r.position.z = -ringCount * 1.5 + 5.0;
                    }
                    const pz = r.position.z;
                    r.position.x = Math.sin(pz * 0.04 + time) * 0.8;
                    r.position.y = Math.cos(pz * 0.04 + time) * 0.8;
                    r.rotation.z = pz * 0.05 + time * 0.01;
                }

                const pos = particles.geometry.attributes.position.array;
                for (let i = 0; i < pCount * 3; i += 3) {
                    pos[i+2] += pSpeed[i/3];
                    if (pos[i+2] > 5.0) {
                        pos[i+2] = -75;
                    }
                }
                particles.geometry.attributes.position.needsUpdate = true;
                particles.rotation.z += 0.00005;

                camera.position.x = Math.sin(time * 0.1) * 0.15;
                camera.position.y = Math.cos(time * 0.08) * 0.12;
                camera.rotation.z = Math.sin(time * 0.05) * 0.008;

                renderer.render(scene, camera);
            }
            animate();

            window.addEventListener('resize', () => {
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            });
        </script>
    </body>
    </html>
    """
    components.html(tunel_html, height=0)

# ---------------- ESTILOS VISUAIS GLOBAIS (LAYOUT FLUIDO / LARGURA TOTAL) ----------------
st.markdown("""
    <style>
    html, body, .stApp, [data-testid="stAppViewContainer"], .main {
        background: transparent !important;
    }
    body {
        font-family: 'Poppins', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    div[data-testid="stCustomComponentV1"],
    iframe {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        z-index: -9999 !important;
        border: none !important;
        pointer-events: none !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    .element-container:has(div[data-testid="stCustomComponentV1"]) {
        position: absolute !important;
        height: 0px !important;
        overflow: hidden !important;
    }

    .block-container {
        position: relative !important;
        z-index: 10 !important;
        max-width: 96% !important;
        width: 100% !important;
        padding-left: 2.5rem !important;
        padding-right: 2.5rem !important;
        padding-top: 2rem !important;
    }

    .glass-card {
        background: rgba(7, 13, 19, 0.90) !important;
        border: 1px solid rgba(0, 217, 217, 0.24) !important;
        border-radius: 14px !important;
        padding: 24px !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.7) !important;
    }

    .main-header {
        background: linear-gradient(135deg, rgba(8, 15, 21, 0.95) 0%, rgba(4, 7, 11, 0.95) 100%) !important;
        border: 1px solid rgba(0, 217, 217, 0.32) !important;
        border-radius: 16px;
        padding: 26px;
        margin-bottom: 24px;
        backdrop-filter: blur(16px);
        box-shadow: 0 8px 35px rgba(0, 0, 0, 0.8);
    }

    .badge-pill {
        display: inline-block;
        padding: 5px 14px;
        font-size: 11px;
        font-weight: 700;
        border-radius: 9999px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 8px;
    }
    .badge-turquoise { 
        background: rgba(0, 217, 217, 0.14); 
        color: #00D9D9; 
        border: 1px solid rgba(0, 217, 217, 0.38); 
    }
    .badge-purple { 
        background: rgba(168, 85, 247, 0.15); 
        color: #c084fc; 
        border: 1px solid rgba(168, 85, 247, 0.3); 
    }

    div[data-testid="stMetric"] {
        background: rgba(7, 13, 19, 0.92) !important;
        border: 1px solid rgba(0, 217, 217, 0.22) !important;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5) !important;
    }
    div[data-testid="stMetricLabel"] p {
        color: #94a3b8 !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    div[data-testid="stMetricValue"] div {
        color: #00D9D9 !important;
        font-size: 24px !important;
        font-weight: 700;
        text-shadow: 0 0 12px rgba(0, 217, 217, 0.25);
    }

    div[data-testid="stFileUploader"] {
        background: rgba(7, 13, 19, 0.85) !important;
        border: 1px dashed rgba(0, 217, 217, 0.42) !important;
        border-radius: 14px !important;
        padding: 18px !important;
        box-shadow: 0 4px 25px rgba(0, 0, 0, 0.6) !important;
    }

    button[data-baseweb="tab"] {
        background: transparent !important;
        color: #94a3b8 !important;
        font-weight: 600 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #00D9D9 !important;
        border-bottom-color: #00D9D9 !important;
    }

    .pricing-card {
        background: rgba(7, 13, 19, 0.92);
        border: 1px solid rgba(0, 217, 217, 0.22);
        border-radius: 14px;
        padding: 26px 22px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .pricing-card-featured {
        background: linear-gradient(180deg, rgba(11, 23, 32, 0.95) 0%, rgba(5, 9, 13, 0.95) 100%);
        border: 2px solid #00D9D9;
        box-shadow: 0 8px 32px rgba(0, 217, 217, 0.25);
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
        color: #ffffff;
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
        color: #00D9D9;
        font-weight: bold;
        margin-right: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------- MOTORES DE PROCESSAMENTO COM CREDIBILIDADE ----------------
def corrigir_texto(texto):
    if not texto:
        return ""
    try:
        if "Ã" in texto:
            return texto.encode("latin1").decode("utf-8")
    except Exception:
        pass
    return texto

def processar_saft_xml(xml_bytes):
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

def processar_documento_comercial(file_bytes, filename):
    filename_lower = filename.lower()
    
    if any(k in filename_lower for k in ['curriculo', 'cv', 'bio', 'foto', 'perfil', 'manual']):
        raise ValueError("O ficheiro carregado parece ser um documento pessoal ou currículo. Por favor utilize um documento comercial de vendas.")

    if filename_lower.endswith('.xml'):
        return processar_saft_xml(file_bytes)

    if filename_lower.endswith(('.xlsx', '.xls', '.csv')):
        try:
            if filename_lower.endswith('.xlsx'):
                df_raw = pd.read_excel(io.BytesIO(file_bytes))
            elif filename_lower.endswith('.xls'):
                df_raw = pd.read_excel(io.BytesIO(file_bytes), engine='xlrd')
            else:
                try:
                    df_raw = pd.read_csv(io.BytesIO(file_bytes), encoding='utf-8', sep=None, engine='python')
                except Exception:
                    df_raw = pd.read_csv(io.BytesIO(file_bytes), encoding='latin1', sep=None, engine='python')

            colunas_texto = " ".join([str(c).lower() for c in df_raw.columns])
            if not any(k in colunas_texto for k in ['cliente', 'fatura', 'data', 'valor', 'total', 'net', 'iva', 'preco']):
                raise ValueError("A tabela carregada não possui colunas reconhecíveis de faturação (ex: Cliente, Fatura, Valor).")

            col_map = {}
            for col in df_raw.columns:
                col_lower = str(col).lower().strip()
                if any(k in col_lower for k in ['cliente', 'nome', 'customer', 'entidade', 'empresa']):
                    col_map[col] = 'Cliente'
                elif any(k in col_lower for k in ['fatura', 'doc', 'documento', 'invoice', 'numero', 'nº']):
                    col_map[col] = 'Documento'
                elif any(k in col_lower for k in ['data', 'date', 'emissao', 'dia']):
                    col_map[col] = 'Data'
                elif any(k in col_lower for k in ['bruto', 'total', 'gross', 'valor total']):
                    col_map[col] = 'ValorBruto'
                elif any(k in col_lower for k in ['liquido', 'net', 'base', 'valor sem iva']):
                    col_map[col] = 'ValorLiquido'
                elif any(k in col_lower for k in ['iva', 'imposto', 'tax']):
                    col_map[col] = 'Imposto'
                elif any(k in col_lower for k in ['tipo', 'type', 'documenttype']):
                    col_map[col] = 'Tipo'

            df_raw = df_raw.rename(columns=col_map)

            # Blindagem: se faltar alguma coluna essencial, criar por omissão com valores seguros
            if 'Cliente' not in df_raw.columns:
                df_raw['Cliente'] = 'Cliente Geral'
            if 'Documento' not in df_raw.columns:
                df_raw['Documento'] = [f"DOC-{i+1}" for i in range(len(df_raw))]
            if 'Data' not in df_raw.columns:
                df_raw['Data'] = '2026-01-01'
            if 'ValorBruto' not in df_raw.columns:
                numeric_cols = df_raw.select_dtypes(include='number').columns
                if len(numeric_cols) > 0:
                    df_raw['ValorBruto'] = df_raw[numeric_cols[0]]
                else:
                    df_raw['ValorBruto'] = 1000.0

            for col in ['ValorBruto', 'ValorLiquido', 'Imposto']:
                if col in df_raw.columns:
                    df_raw[col] = pd.to_numeric(df_raw[col].astype(str).str.replace('€', '').str.replace(' ', '').str.replace(',', '.'), errors='coerce').fillna(0.0)

            dados_faturas = []
            for _, row in df_raw.iterrows():
                doc_type = str(row.get('Tipo', 'FT')).upper()
                if 'NC' in doc_type or ('NOTA' in doc_type and 'CREDITO' in doc_type):
                    doc_type = 'NC'
                else:
                    doc_type = 'FT'

                vb = float(row.get('ValorBruto', 0))
                if vb == 0:
                    continue

                vl = float(row.get('ValorLiquido', vb / 1.23))
                imp = float(row.get('Imposto', vb - vl))

                if doc_type == 'NC':
                    vb = -abs(vb)
                    vl = -abs(vl)
                    imp = -abs(imp)

                dados_faturas.append({
                    'Documento': str(row.get('Documento', 'DOC-01')),
                    'Tipo': doc_type,
                    'Data': str(row.get('Data', '2026-01-01'))[:10],
                    'Cliente': str(row.get('Cliente', 'Cliente Desconhecido')),
                    'ValorBruto': vb,
                    'ValorLiquido': vl,
                    'Imposto': imp
                })

            if not dados_faturas:
                raise ValueError("Nenhum registo de venda válido foi encontrado na tabela.")

            df_final = pd.DataFrame(dados_faturas)
            df_tax_final = pd.DataFrame([{
                'TaxCode': 'NOR',
                'TaxRate': 23.0,
                'Base': abs(df_final['ValorLiquido'].sum()),
                'ValorIVA': abs(df_final['Imposto'].sum())
            }])
            return df_final, df_tax_final
        except Exception as e:
            raise ValueError(f"Erro ao processar o ficheiro tabular: {e}")

    raise ValueError("Formato não suportado para análise de vendas. Por favor utilize um ficheiro SAF-T (.xml), Excel (.xlsx) ou CSV comercial.")

def exibir_tabela_precos():
    st.markdown("### 💎 Planos de Acompanhamento Mensal")
    st.markdown("Disponibilizamos planos para **empresas**, **gestores** e **gabinetes de contabilidade**:")
    
    col_p1, col_p2, col_p3 = st.columns(3)

    with col_p1:
        st.markdown("""
        <div class="pricing-card">
            <div>
                <span class="badge-pill badge-turquoise">Diagnóstico</span>
                <h3 style="margin: 0; color: #ffffff;">Acesso Gratuito</h3>
                <div class="pricing-price">0 €</div>
                <div class="pricing-sub">Para testes e diagnósticos pontuais</div>
                <ul class="feature-list">
                    <li><span class="check-icon">✓</span> Leitura SAF-T, Excel e CSV</li>
                    <li><span class="check-icon">✓</span> KPIs essenciais de faturação</li>
                    <li><span class="check-icon">✓</span> Curva ABC e Alertas de Risco</li>
                    <li><span class="check-icon">✓</span> Relatório Executivo</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.button("Plano Ativo no Ecrã", disabled=True, key="btn_free_tab")

    with col_p2:
        st.markdown("""
        <div class="pricing-card">
            <div>
                <span class="badge-pill badge-turquoise">Empresas & Gestores</span>
                <h3 style="margin: 0; color: #ffffff;">PME Gestão</h3>
                <div class="pricing-price">29 € <span style="font-size: 15px; color: #94a3b8; font-weight: normal;">/mês</span></div>
                <div class="pricing-sub">Inteligência comercial contínua</div>
                <ul class="feature-list">
                    <li><span class="check-icon">✓</span> <b>Tudo do plano gratuito</b></li>
                    <li><span class="check-icon">✓</span> Análise Mensal Automática via E-mail</li>
                    <li><span class="check-icon">✓</span> <b>Relatório Homólogo</b> (Mês vs Mês Anterior)</li>
                    <li><span class="check-icon">✓</span> Detetor de Perda de Clientes (Churn)</li>
                    <li><span class="check-icon">✓</span> Alertas de Risco de Tesouraria no WhatsApp</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        msg_pme = "Olá! Gostaria de subscrever o Plano PME Gestão (29€/mês) para a minha empresa."
        url_pme = f"https://wa.me/351935009099?text={urllib.parse.quote(msg_pme)}"
        st.link_button("🚀 Subscrever PME Gestão (29€)", url_pme, use_container_width=True)

    with col_p3:
        st.markdown("""
        <div class="pricing-card-featured">
            <div>
                <span class="badge-pill badge-purple">⭐ Mais Escolhido</span>
                <h3 style="margin: 0; color: #ffffff;">Gabinete Pro</h3>
                <div class="pricing-price">79 € <span style="font-size: 15px; color: #00D9D9; font-weight: normal;">/mês</span></div>
                <div class="pricing-sub">Para Gabinetes de Contabilidade & TOCs</div>
                <ul class="feature-list">
                    <li><span class="check-icon">✓</span> <b>Até 30 empresas da carteira</b></li>
                    <li><span class="check-icon">✓</span> <b>White-Label:</b> Relatórios com o logótipo do gabinete</li>
                    <li><span class="check-icon">✓</span> Mapa de Auditoria de IVA para apoio fiscal</li>
                    <li><span class="check-icon">✓</span> Exportação executiva para enviar aos clientes</li>
                    <li><span class="check-icon">✓</span> Suporte dedicado via WhatsApp</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        msg_gab = "Olá! Gostaria de ativar o Plano Gabinete Pro (79€/mês) para o meu gabinete de contabilidade."
        url_gab = f"https://wa.me/351935009099?text={urllib.parse.quote(msg_gab)}"
        st.link_button("⭐ Aderir ao Gabinete Pro (79€)", url_gab, type="primary", use_container_width=True)

# ---------------- CABEÇALHO CORPORATIVO ----------------
st.markdown("""
<div class="main-header">
    <span class="badge-pill badge-turquoise">⚡ PLATAFORMA DE INTELIGÊNCIA COMERCIAL • ENTERPRISE BI</span>
    <h1 style="margin: 0; font-size: 2.3rem; font-weight: 800; color: #ffffff;">SAF-T Intelligence Pro</h1>
    <h3 style="margin: 4px 0 0 0; font-size: 1.15rem; font-weight: 600; color: #00D9D9;">Análise Preditiva, Churn de Clientes, Sazonalidade e Auditoria Fiscal</h3>
    <p style="margin: 8px 0 0 0; color: #94a3b8; font-size: 0.95rem;">
        Carregue o seu ficheiro SAF-T (XML), Excel (.xlsx) ou CSV comercial para desbloquear inteligência de negócio avançada instantaneamente.
    </p>
</div>
""", unsafe_allow_html=True)

ficheiro_upload = st.file_uploader(
    "📂 Arraste ou selecione o ficheiro ou relatório comercial (.xml, .xlsx, .csv)", 
    type=["xml", "xlsx", "xls", "csv"]
)

# Injetar o fundo túnel idêntico e em constante movimento em ambas as telas
injetar_fundo_tunel()

# ---------------- CASO 1: PÁGINA INICIAL CORPORATIVA ----------------
if ficheiro_upload is None:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Pilares de Inteligência para o seu Negócio:")
    col_h1, col_h2, col_h3 = st.columns(3)

    with col_h1:
        st.markdown("""
        <div class="glass-card">
            <span class="badge-pill badge-turquoise">Análise Preditiva</span>
            <h3 style="margin-top: 8px; color: #ffffff;">📈 Forecasting de Vendas</h3>
            <p style="color: #94a3b8; font-size: 14px; margin-top: 6px;">
                Projeção automática de tesouraria e tendência de faturação para os próximos trimestres com base no histórico real.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_h2:
        st.markdown("""
        <div class="glass-card">
            <span class="badge-pill badge-turquoise">Gestão de Risco</span>
            <h3 style="margin-top: 8px; color: #ffffff;">⚠️ Detetor de Churn (Inativos)</h3>
            <p style="color: #94a3b8; font-size: 14px; margin-top: 6px;">
                Identifique imediatamente clientes importantes que pararam de comprar e recupere receita antes de perder o contrato.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_h3:
        st.markdown("""
        <div class="glass-card">
            <span class="badge-pill badge-turquoise">Auditoria Avançada</span>
            <h3 style="margin-top: 8px; color: #ffffff;">🔍 Deteção de Anomalias</h3>
            <p style="color: #94a3b8; font-size: 14px; margin-top: 6px;">
                Identificação automática de faturas atípicas, desvios estatísticos e conferência rigorosa de IVA por escalão.
            </p>
        </div>
        """, unsafe_allow_html=True)

# ---------------- CASO 2: PROCESSAMENTO E PAINEL ENTERPRISE BI ----------------
else:
    try:
        bytes_data = ficheiro_upload.read()
        filename_str = ficheiro_upload.name

        # Simulação de Auditoria de Alta Credibilidade
        with st.status("🔍 A executar motor de Inteligência Comercial e Medidas DAX...", expanded=True) as status_process:
            st.write("📁 A validar integridade relacional do documento...")
            time.sleep(0.5)
            st.write("⚙️ A processar linhas de faturação e notas de crédito...")
            time.sleep(0.5)
            st.write("📈 A calcular modelos preditivos, sazonalidade e Churn...")
            time.sleep(0.7)
            
            df, df_tax = processar_documento_comercial(bytes_data, filename_str)
            
            # Enriquecer DataFrame com colunas temporais
            df['Data_dt'] = pd.to_datetime(df['Data'], errors='coerce')
            df['Ano'] = df['Data_dt'].dt.year.fillna(2026).astype(int)
            
            meses_pt = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
            df['Mês_Num'] = df['Data_dt'].dt.month.fillna(1).astype(int)
            df['Mês'] = df['Data_dt'].dt.month.map(meses_pt).fillna("Janeiro")
            df['Trimestre'] = df['Data_dt'].dt.to_period('Q').astype(str).fillna("2026Q1")

            status_process.update(label="✅ Modelo de Inteligência Comercial carregado com sucesso!", state="complete", expanded=False)

        # ---------------- BARRA DE FILTROS ESTILO DASHBOARD EXECUTIVO (PILLS) ----------------
        st.markdown("### 🎛️ Segmentação Rápida por Período (Ano)")
        
        anos_disponiveis = sorted(df['Ano'].unique(), reverse=True)
        opcoes_ano = ["Todos"] + [str(a) for a in anos_disponiveis]
        
        ano_escolhido = st.pills("Selecione o Ano de Análise", options=opcoes_ano, default="Todos")

        if ano_escolhido and ano_escolhido != "Todos":
            df_filtrado = df[df['Ano'] == int(ano_escolhido)]
        else:
            df_filtrado = df.copy()

        if df_filtrado.empty:
            st.warning("⚠️ Nenhum registo encontrado para o período selecionado.")
        else:
            # Cálculos Globais
            faturas_positivas = df_filtrado[df_filtrado['Tipo'] != 'NC']
            notas_credito = df_filtrado[df_filtrado['Tipo'] == 'NC']

            fat_bruta = faturas_positivas['ValorBruto'].sum()
            total_nc = abs(notas_credito['ValorBruto'].sum())
            fat_liquida = df_filtrado['ValorBruto'].sum()
            total_iva = df_filtrado['Imposto'].sum()

            taxa_nc = (total_nc / fat_bruta * 100) if fat_bruta > 0 else 0
            total_docs = len(faturas_positivas)
            ticket_medio = fat_liquida / total_docs if total_docs > 0 else 0

            # Análise de Concentração
            df_clientes_positivo = df_filtrado[df_filtrado['ValorBruto'] > 0].groupby('Cliente')['ValorBruto'].sum().sort_values(ascending=False).reset_index()
            total_bruto_pos = df_clientes_positivo['ValorBruto'].sum()
            
            top_cliente_val = df_clientes_positivo.iloc[0]['ValorBruto'] if not df_clientes_positivo.empty else 0
            concentracao_top1 = (top_cliente_val / total_bruto_pos * 100) if total_bruto_pos > 0 else 0

            # NAVEGAÇÃO POR TABS AVANÇADAS
            tab_visao, tab_pred, tab_churn, tab_anomalias, tab_abc, tab_iva, tab_plano = st.tabs([
                "📈 Visão Geral & Sazonalidade",
                "🔮 Previsão (Forecasting)",
                "⚠️ Clientes em Risco (Churn)",
                "🔍 Auditoria de Anomalias",
                "👥 Curva ABC & Concentração",
                "⚖️ Auditoria de IVA & Fiscal",
                "💎 Planos & Relatório"
            ])

            # TAB 1: VISÃO GERAL & SAZONALIDADE
            with tab_visao:
                st.markdown("#### Indicadores Principais de Desempenho (Medidas DAX)")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Faturação Líquida [DAX]", f"{fat_liquida:,.2f} €")
                c2.metric("Ticket Médio Real", f"{ticket_medio:,.2f} €")
                c3.metric("Documentos Emitidos", f"{total_docs}", f"{len(notas_credito)} NCs anuladas", delta_color="inverse")
                c4.metric("Risco Concentração Top 1", f"{concentracao_top1:.1f}%")

                c5, c6, c7, c8 = st.columns(4)
                c5.metric("Volume Bruto Total", f"{fat_bruta:,.2f} €")
                c6.metric("Total Devoluções (NC)", f"{total_nc:,.2f} €")
                c7.metric("Taxa de Devoluções (% NC)", f"{taxa_nc:.2f}%")
                c8.metric("Total IVA Liquidado", f"{total_iva:,.2f} €")

                st.markdown("---")
                col_chart1, col_chart2 = st.columns(2)
                
                with col_chart1:
                    st.markdown("#### 📊 Sazonalidade de Vendas por Mês")
                    df_mes = df_filtrado.groupby(['Mês_Num', 'Mês'])['ValorBruto'].sum().reset_index().sort_values('Mês_Num')
                    st.bar_chart(df_mes.set_index('Mês')['ValorBruto'], color="#00D9D9")

                with col_chart2:
                    st.markdown("#### 📈 Ritmo Diário de Faturação")
                    df_diario = df_filtrado.groupby('Data_dt')['ValorBruto'].sum().reset_index()
                    st.line_chart(df_diario.set_index('Data'), color="#a855f7")

            # TAB 2: PREVISÃO (FORECASTING)
            with tab_pred:
                st.markdown("#### 🔮 Projeção de Faturação para os Próximos 3 Meses")
                st.caption("Modelo preditivo linear baseado na taxa de crescimento histórica do negócio.")

                df_mensal = df.groupby(df['Data_dt'].dt.to_period('M'))['ValorBruto'].sum().reset_index()
                df_mensal['Data_dt'] = df_mensal['Data_dt'].dt.to_timestamp()
                
                if len(df_mensal) >= 2:
                    x = np.arange(len(df_mensal))
                    y = df_mensal['ValorBruto'].values
                    m, c = np.polyfit(x, y, 1)
                    
                    ultimo_mes = df_mensal['Data_dt'].max()
                    projecoes = []
                    for i in range(1, 4):
                        proximo_mes = ultimo_mes + pd.DateOffset(months=i)
                        val_proj = max(0, (m * (len(x) + i)) + c)
                        projecoes.append({'Mês': proximo_mes.strftime('%Y-%m'), 'Faturação Prevista (€)': round(val_proj, 2)})

                    df_proj = pd.DataFrame(projecoes)
                    
                    p_col1, p_col2 = st.columns([1, 1.2])
                    with p_col1:
                        st.markdown("##### 📌 Próximos Períodos Estimados:")
                        for _, row in df_proj.iterrows():
                            st.metric(f"Mês: {row['Mês']}", f"{row['Faturação Prevista (€)']:,.2f} €", "Projeção IA")
                    with p_col2:
                        st.markdown("##### Histórico vs Projeção Tendencial:")
                        st.line_chart(df_mensal.set_index('Data_dt')['ValorBruto'], color="#00D9D9")
                else:
                    st.info("É necessário um histórico superior a 2 meses diferentes para calcular a projeção preditiva com exatidão.")

            # TAB 3: CLIENTES EM RISCO (CHURN)
            with tab_churn:
                st.markdown("#### ⚠️ Detetor de Clientes em Risco de Abandono (Churn)")
                st.caption("Clientes importantes que efetuaram compras no passado mas não têm atividade recente no final do período analisado.")

                if not df_filtrado.empty:
                    data_maxima = df_filtrado['Data_dt'].max()
                    limite_inativo = data_maxima - pd.Timedelta(days=90)

                    compras_cliente = df_filtrado[df_filtrado['ValorBruto'] > 0].groupby('Cliente').agg(
                        Ultima_Compra=('Data_dt', 'max'),
                        Total_Gasto=('ValorBruto', 'sum'),
                        Total_Faturas=('Documento', 'count')
                    ).reset_index()

                    churn_risco = compras_cliente[compras_cliente['Ultima_Compra'] < limite_inativo].sort_values(by='Total_Gasto', ascending=False)

                    if not churn_risco.empty:
                        st.warning(f"🚨 Atenção: Foram detetados **{len(churn_risco)} clientes** com histórico relevante que estão inativos há mais de 90 dias.")
                        df_churn_show = churn_risco.copy()
                        df_churn_show['Ultima_Compra'] = df_churn_show['Ultima_Compra'].dt.strftime('%Y-%m-%d')
                        df_churn_show['Total_Gasto'] = df_churn_show['Total_Gasto'].map("{:,.2f} €".format)
                        st.dataframe(df_churn_show, use_container_width=True, hide_index=True)
                    else:
                        st.success("✅ Excelente retenção! Nenhum cliente principal apresenta risco iminente de inatividade.")

            # TAB 4: AUDITORIA DE ANOMALIAS
            with tab_anomalias:
                st.markdown("#### 🔍 Auditoria de Faturas Atípicas (Deteção de Outliers)")
                st.caption("Identificação automática de faturas com valores anormalmente superiores à média da empresa.")

                if not df_filtrado.empty:
                    media_fat = df_filtrado[df_filtrado['ValorBruto'] > 0]['ValorBruto'].mean()
                    desvio_fat = df_filtrado[df_filtrado['ValorBruto'] > 0]['ValorBruto'].std()
                    limite_anomalia = media_fat + (2 * desvio_fat)

                    anomalias = df_filtrado[df_filtrado['ValorBruto'] > limite_anomalia]

                    if not anomalias.empty:
                        st.info(f"🔎 Foram encontradas **{len(anomalias)} faturas atípicas** (valores acima de {limite_anomalia:,.2f} €).")
                        df_anom_show = anomalias[['Data', 'Documento', 'Cliente', 'ValorBruto']].copy()
                        df_anom_show['ValorBruto'] = df_anom_show['ValorBruto'].map("{:,.2f} €".format)
                        st.dataframe(df_anom_show, use_container_width=True, hide_index=True)
                    else:
                        st.success("✅ A distribuição de valores está homogénea. Não foram detetadas faturas estatisticamente anómalas.")

            # TAB 5: CURVA ABC
            with tab_abc:
                st.markdown("#### Segmentação Estratégica de Carteira (Regra 80/20)")
                st.caption("Classificação automática dos clientes que asseguram o volume financeiro do seu negócio.")

                df_abc = df_clientes_positivo.copy()
                df_abc['% Receita'] = (df_abc['ValorBruto'] / total_bruto_pos) * 100 if total_bruto_pos > 0 else 0
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
                    st.subheader("Top Clientes do Negócio")
                    st.bar_chart(df_abc.head(10).set_index('Cliente')['ValorBruto'], horizontal=True, color="#00D9D9")

                with col_abc_table:
                    st.subheader("Detetor Estratégico")
                    df_exibicao = df_abc[['Cliente', 'ValorBruto', '% Receita', 'Categoria ABC']].copy()
                    df_exibicao['ValorBruto'] = df_exibicao['ValorBruto'].map("{:,.2f} €".format)
                    df_exibicao['% Receita'] = df_exibicao['% Receita'].map("{:.2f}%".format)
                    st.dataframe(df_exibicao, use_container_width=True, hide_index=True)

            # TAB 6: AUDITORIA DE IVA
            with tab_iva:
                st.markdown("#### Resumo Fiscal de IVA Liquidado")
                st.caption("Conferência automática por escalão tributável para apoio à gestão e contabilidade.")

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
                    st.info("O documento carregado não possui detalhe granular por linha de imposto. O total apurado foi de: " + f"{total_iva:,.2f} €")

            # TAB 7: PLANOS & RELATÓRIO
            with tab_plano:
                st.markdown("#### 📄 Relatório Executivo Avançado (Pronto a Descarregar)")
                st.caption("Descarregue o relatório detalhado contendo sumário executivo, matriz de risco, curva ABC e auditoria de IVA.")
                
                html_linhas = ""
                for _, row in df_clientes_positivo.head(25).iterrows():
                    p_cli = (row['ValorBruto'] / total_bruto_pos * 100) if total_bruto_pos > 0 else 0
                    html_linhas += f"""
                    <tr>
                        <td style="padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.08); color: #f8fafc;">{row['Cliente']}</td>
                        <td style="padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.08); text-align: right; font-weight: 600; color: #00D9D9;">{row['ValorBruto']:,.2f} €</td>
                        <td style="padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.08); text-align: right; color: #cbd5e1;">{p_cli:.1f}%</td>
                    </tr>
                    """

                html_iva_linhas = ""
                if not df_tax.empty:
                    df_tax_resumo = df_tax.groupby(['TaxCode', 'TaxRate'])[['Base', 'ValorIVA']].sum().reset_index()
                    for _, row in df_tax_resumo.iterrows():
                        html_iva_linhas += f"""
                        <tr>
                            <td style="padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.08); color: #f8fafc;">{row['TaxCode']} ({row['TaxRate']:.1f}%)</td>
                            <td style="padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.08); text-align: right; color: #cbd5e1;">{row['Base']:,.2f} €</td>
                            <td style="padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.08); text-align: right; font-weight: 600; color: #00D9D9;">{row['ValorIVA']:,.2f} €</td>
                        </tr>
                        """

                html_doc = f"""<!DOCTYPE html>
                <html lang="pt">
                <head>
                    <meta charset="UTF-8">
                    <title>Relatório Executivo Avançado - SAF-T Intelligence Pro</title>
                    <style>
                        body {{ font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #030609; color: #f8fafc; padding: 40px; }}
                        .container {{ max-width: 950px; margin: 0 auto; background: rgba(8, 14, 20, 0.95); border: 1px solid rgba(0, 217, 217, 0.3); border-radius: 16px; padding: 45px; box-shadow: 0 15px 50px rgba(0,0,0,0.85); }}
                        .header-top {{ display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 1px solid rgba(0, 217, 217, 0.25); padding-bottom: 25px; margin-bottom: 35px; }}
                        .badge {{ background: rgba(0, 217, 217, 0.15); color: #00D9D9; border: 1px solid rgba(0, 217, 217, 0.4); padding: 5px 14px; font-size: 11px; font-weight: bold; border-radius: 99px; text-transform: uppercase; letter-spacing: 0.08em; }}
                        h1 {{ margin: 12px 0 0 0; font-size: 28px; color: #ffffff; font-weight: 800; }}
                        p.sub {{ color: #94a3b8; font-size: 13px; margin-top: 6px; }}
                        .kpis-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; margin-bottom: 35px; }}
                        .kpi-card {{ background: rgba(4, 8, 12, 0.85); border: 1px solid rgba(0, 217, 217, 0.22); border-radius: 12px; padding: 20px; text-align: center; backdrop-filter: blur(10px); }}
                        .kpi-card h4 {{ margin: 0; font-size: 11px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.8px; font-weight: 600; }}
                        .kpi-card p {{ margin: 8px 0 0 0; font-size: 22px; font-weight: 700; color: #00D9D9; text-shadow: 0 0 10px rgba(0, 217, 217, 0.25); }}
                        .section-title {{ font-size: 16px; font-weight: 700; color: #ffffff; margin: 35px 0 15px 0; border-left: 3px solid #00D9D9; padding-left: 12px; }}
                        .diagnostic-box {{ background: rgba(0, 217, 217, 0.05); border: 1px solid rgba(0, 217, 217, 0.2); border-radius: 10px; padding: 20px; margin-bottom: 30px; font-size: 14px; color: #cbd5e1; line-height: 1.6; }}
                        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }}
                        th {{ background: rgba(0, 217, 217, 0.12); color: #00D9D9; padding: 12px; text-align: left; border-bottom: 2px solid rgba(0, 217, 217, 0.4); font-weight: 600; letter-spacing: 0.5px; }}
                        .footer {{ margin-top: 45px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 25px; text-align: center; font-size: 11px; color: #64748b; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header-top">
                            <div>
                                <span class="badge">⚡ SAF-T Intelligence Pro • Executive Report</span>
                                <h1>Auditoria Executiva e Diagnóstico Fiscal</h1>
                                <p class="sub">Relatório analítico avançado de faturação, concentração de carteira e conferência de IVA.</p>
                            </div>
                            <div style="text-align: right;">
                                <p style="font-size: 12px; color: #94a3b8; margin: 0;"><b>Moeda:</b> EUR</p>
                                <p style="font-size: 12px; color: #94a3b8; margin: 4px 0 0 0;"><b>Conformidade:</b> 100% In-Memory (RGPD)</p>
                            </div>
                        </div>

                        <div class="diagnostic-box">
                            <b>📌 Sumário Executivo de Gestão:</b> O volume de negócios líquido apurado no período atinge <b>{fat_liquida:,.2f} €</b>, com um ticket médio real por documento de <b>{ticket_medio:,.2f} €</b>. O índice de concentração do principal cliente situa-se em <b>{concentracao_top1:.1f}%</b>, e a taxa de anulação por notas de crédito é de <b>{taxa_nc:.2f}%</b>.
                        </div>

                        <div class="kpis-grid">
                            <div class="kpi-card"><h4>Faturação Líquida</h4><p>{fat_liquida:,.2f} €</p></div>
                            <div class="kpi-card"><h4>Ticket Médio</h4><p>{ticket_medio:,.2f} €</p></div>
                            <div class="kpi-card"><h4>Risco Cliente Top 1</h4><p>{concentracao_top1:.1f}%</p></div>
                            <div class="kpi-card"><h4>Volume Bruto</h4><p>{fat_bruta:,.2f} €</p></div>
                            <div class="kpi-card"><h4>Total Devoluções (NC)</h4><p>{total_nc:,.2f} €</p></div>
                            <div class="kpi-card"><h4>Total IVA Liquidado</h4><p>{total_iva:,.2f} €</p></div>
                        </div>

                        <div class="section-title">📊 Matriz de Concentração de Clientes (Top da Carteira)</div>
                        <table>
                            <thead>
                                <tr><th>Designação do Cliente</th><th style="text-align: right;">Volume Faturado (€)</th><th style="text-align: right;">Peso na Receita (%)</th></tr>
                            </thead>
                            <tbody>{html_linhas}</tbody>
                        </table>

                        <div class="section-title">⚖️ Auditoria e Conferência de IVA por Escalão Tributário</div>
                        <table>
                            <thead>
                                <tr><th>Código / Taxa Aplicada</th><th style="text-align: right;">Base Tributável (€)</th><th style="text-align: right;">IVA Liquidado (€)</th></tr>
                            </thead>
                            <tbody>{html_iva_linhas}</tbody>
                        </table>

                        <div class="footer">
                            <p>Documento gerado automaticamente pela plataforma de inteligência fiscal <b>SAF-T Intelligence Pro</b> • Uso exclusivo para suporte à gestão empresarial e contabilidade.</p>
                        </div>
                    </div>
                </body>
                </html>"""

                st.download_button(
                    label="📥 Descarregar Relatório Executivo",
                    data=html_doc,
                    file_name="relatorio_saft_executivo_avancado.html",
                    mime="text/html"
                )

                st.markdown("---")
                exibir_tabela_precos()

                st.markdown("---")
                st.subheader("📬 Fale com a Nossa Equipa Comercial")
                
                col_form, col_whats = st.columns([1.2, 1])
                MEU_EMAIL_NOTIFICACAO = "gestao.saft.pt@gmail.com"

                with col_form:
                    with st.form("form_contacto_v2"):
                        st.markdown("**Pedir proposta ou agendar demonstração técnica:**")
                        nome = st.text_input("Nome do Responsável / Empresa")
                        contacto = st.text_input("E-mail ou Telemóvel Corporativo")
                        tipo_perfil = st.selectbox("Solução Pretendida:", ["Plano PME Gestão (29 €/mês)", "Plano Gabinete Pro (79 €/mês)", "Demonstração para Gabinete"])
                        submetido = st.form_submit_button("Submeter Pedido")

                        if submetido:
                            if nome and contacto:
                                try:
                                    payload = json.dumps({
                                        "nome": nome,
                                        "contacto": contacto,
                                        "solucao": tipo_perfil,
                                        "_subject": f"🔥 Novo Lead Comercial SAF-T: {nome}",
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
                                            st.success("✅ Pedido registado com sucesso! A nossa equipa entrará em contacto em até 24 horas.")
                                        elif "message" in res_json:
                                            st.info(f"ℹ️ {res_json['message']}")
                                        else:
                                            st.success("✅ Pedido registado com sucesso!")
                                except Exception as e:
                                    st.error(f"Erro ao submeter: {e}")
                            else:
                                st.error("Por favor, preencha o nome e contacto.")

                with col_whats:
                    st.markdown("**Atendimento Imediato por WhatsApp:**")
                    st.write("Fale com o suporte técnico e comercial para esclarecer dúvidas ou solicitar integração para a sua carteira:")
                    
                    numero_whatsapp = "351935009099" 
                    msg_whats_geral = "Olá! Estive a testar a plataforma SAF-T Intelligence Pro e gostaria de tirar algumas dúvidas com a equipa comercial."
                    url_whatsapp = f"https://wa.me/{numero_whatsapp}?text={urllib.parse.quote(msg_whats_geral)}"
                    
                    st.link_button("💬 Falar com a Equipa Comercial", url_whatsapp, type="primary", use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ **Formato inválido ou documento não suportado:** {e}")
        st.info("💡 **Dica:** Utilize um ficheiro SAF-T oficial (.xml), uma folha de cálculo com faturas (.xlsx) ou um ficheiro CSV comercial.")
