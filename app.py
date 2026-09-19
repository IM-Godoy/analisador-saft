import streamlit as st
import streamlit.components.v1 as components
import xml.etree.ElementTree as ET
import pandas as pd
import urllib.parse
import urllib.request
import json

st.set_page_config(
    page_title="SAF-T Intelligence Pro | Plataforma Executiva B2B", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- MOTOR 3D: IRIDESCENT OIL-SLICK PARTICLE BULGE ON HOVER ----------------
def injetar_fundo_iridescente_3d():
    oil_slick_html = """
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
            scene.fog = new THREE.FogExp2(0x030609, 0.032);

            const camera = new THREE.PerspectiveCamera(48, window.innerWidth / window.innerHeight, 0.1, 100);
            camera.position.set(0, -0.6, 7.8);
            camera.lookAt(0, 0, 0);

            const renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

            // Grelha de partículas de alta densidade
            const gridWidth = 32;
            const gridHeight = 20;
            const segmentsX = 180;
            const segmentsY = 110;
            const geometry = new THREE.PlaneGeometry(gridWidth, gridHeight, segmentsX, segmentsY);

            // Vertex Shader: Ondulação orgânica contínua + Deformação Bulge sob o cursor
            const vertexShader = `
                uniform float uTime;
                uniform vec2 uMouse;
                uniform float uBulgeRadius;
                uniform float uBulgeStrength;

                varying vec2 vUv;
                varying float vElevation;
                varying float vDist;

                void main() {
                    vUv = uv;
                    vec3 pos = position;

                    // Movimento ondulatório fluido suave (oil-slick surface)
                    float wave1 = sin(pos.x * 0.40 + uTime * 0.65) * cos(pos.y * 0.40 + uTime * 0.50) * 0.38;
                    float wave2 = sin(pos.x * 0.85 - uTime * 0.35 + pos.y * 0.55) * 0.16;

                    // Cálculo da deformação 3D (Bulge) sob o cursor
                    float dist = distance(pos.xy, uMouse);
                    vDist = dist;
                    float bulge = smoothstep(uBulgeRadius, 0.0, dist);
                    bulge = pow(bulge, 1.8) * uBulgeStrength;

                    pos.z += wave1 + wave2 + bulge;
                    vElevation = pos.z;

                    vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
                    // Aumenta ligeiramente a partícula no topo do bulge
                    gl_PointSize = (18.5 / -mvPosition.z) * (1.0 + bulge * 0.85);
                    gl_Position = projectionMatrix * mvPosition;
                }
            `;

            // Fragment Shader: Paleta iridescente de óleo (Turquesa #00D9D9, Petróleo, Violeta e Ouro)
            const fragmentShader = `
                uniform float uTime;
                varying vec2 vUv;
                varying float vElevation;
                varying float vDist;

                vec3 palette(float t) {
                    // Cosine color palette calibrada para o efeito mancha de óleo
                    vec3 a = vec3(0.20, 0.60, 0.70);
                    vec3 b = vec3(0.35, 0.38, 0.38);
                    vec3 c = vec3(0.85, 0.95, 1.15);
                    vec3 d = vec3(0.02, 0.26, 0.52);
                    return a + b * cos(6.28318 * (c * t + d));
                }

                void main() {
                    // Ponto circular com brilho radial suave
                    float distCenter = length(gl_PointCoord - vec2(0.5));
                    if (distCenter > 0.5) discard;
                    float alpha = smoothstep(0.5, 0.06, distCenter);

                    // Gradiente iridescente reativo à altura e ao movimento
                    float t = vElevation * 0.42 + vUv.x * 0.22 + sin(uTime * 0.22) * 0.12;
                    vec3 col = palette(t);

                    // Reflexo iridescente especular no ápice do bulge
                    float sheen = smoothstep(2.8, 0.0, vDist) * 0.45;
                    col += vec3(0.12, 0.40, 0.40) * sheen;

                    gl_FragColor = vec4(col, alpha * 0.76);
                }
            `;

            const material = new THREE.ShaderMaterial({
                vertexShader: vertexShader,
                fragmentShader: fragmentShader,
                uniforms: {
                    uTime: { value: 0 },
                    uMouse: { value: new THREE.Vector2(-100, -100) },
                    uBulgeRadius: { value: 4.2 },
                    uBulgeStrength: { value: 2.4 }
                },
                transparent: true,
                depthWrite: false,
                blending: THREE.AdditiveBlending
            });

            const particles = new THREE.Points(geometry, material);
            particles.rotation.x = -0.36; // Perspetiva suave do horizonte
            scene.add(particles);

            // Plano invisível para intersecção de raio (Raycasting preciso)
            const hitPlane = new THREE.Mesh(
                new THREE.PlaneGeometry(45, 30),
                new THREE.MeshBasicMaterial({ visible: false })
            );
            hitPlane.rotation.x = -0.36;
            scene.add(hitPlane);

            // Deteção suave do rato com interpolação (Lerp)
            const raycaster = new THREE.Raycaster();
            const mouseScreen = new THREE.Vector2(-10, -10);
            const targetPos = new THREE.Vector2(-100, -100);
            const currentPos = new THREE.Vector2(-100, -100);

            function updatePointer(clientX, clientY, w, h) {
                mouseScreen.x = (clientX / w) * 2 - 1;
                mouseScreen.y = -(clientY / h) * 2 + 1;
                raycaster.setFromCamera(mouseScreen, camera);
                const hits = raycaster.intersectObject(hitPlane);
                if (hits.length > 0) {
                    const localPt = particles.worldToLocal(hits[0].point.clone());
                    targetPos.set(localPt.x, localPt.y);
                }
            }

            // Captura eventos do rato mesmo por cima dos cartões de interface
            try {
                window.parent.addEventListener('mousemove', (e) => {
                    updatePointer(e.clientX, e.clientY, window.parent.innerWidth, window.parent.innerHeight);
                });
                window.parent.addEventListener('touchmove', (e) => {
                    if (e.touches.length > 0) {
                        updatePointer(e.touches[0].clientX, e.touches[0].clientY, window.parent.innerWidth, window.parent.innerHeight);
                    }
                });
            } catch (err) {
                window.addEventListener('mousemove', (e) => {
                    updatePointer(e.clientX, e.clientY, window.innerWidth, window.innerHeight);
                });
            }

            // Loop de Renderização a 60 FPS
            let clock = new THREE.Clock();
            function animate() {
                requestAnimationFrame(animate);
                const elapsedTime = clock.getElapsedTime();
                material.uniforms.uTime.value = elapsedTime;

                // Amortecimento suave na subida e movimento do bulge
                currentPos.lerp(targetPos, 0.08);
                material.uniforms.uMouse.value.copy(currentPos);

                // Flutuação subtil da câmara
                camera.position.x = Math.sin(elapsedTime * 0.25) * 0.15;
                camera.position.y = -0.6 + Math.cos(elapsedTime * 0.20) * 0.12;

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
    components.html(oil_slick_html, height=0)

injetar_fundo_iridescente_3d()

# ---------------- ESTILOS VISUAIS: DARK GLASSMORPHISM TURQUESA ----------------
st.markdown("""
    <style>
    /* Transparência Global */
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main {
        background: transparent !important;
    }
    body {
        background-color: #030609 !important;
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
        max-width: 1200px !important;
        padding-top: 2rem !important;
    }

    /* Cartões Glassmorphism Translúcidos */
    .glass-card {
        background: rgba(7, 13, 19, 0.82) !important;
        border: 1px solid rgba(0, 217, 217, 0.24) !important;
        border-radius: 14px !important;
        padding: 24px !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6) !important;
    }

    .main-header {
        background: linear-gradient(135deg, rgba(8, 15, 21, 0.9) 0%, rgba(4, 7, 11, 0.9) 100%) !important;
        border: 1px solid rgba(0, 217, 217, 0.32) !important;
        border-radius: 16px;
        padding: 26px;
        margin-bottom: 24px;
        backdrop-filter: blur(16px);
        box-shadow: 0 8px 35px rgba(0, 0, 0, 0.7);
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

    /* Cartões de Métricas */
    div[data-testid="stMetric"] {
        background: rgba(7, 13, 19, 0.84) !important;
        border: 1px solid rgba(0, 217, 217, 0.22) !important;
        padding: 16px;
        border-radius: 12px;
        backdrop-filter: blur(14px) !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.45) !important;
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
        background: rgba(7, 13, 19, 0.78) !important;
        border: 1px dashed rgba(0, 217, 217, 0.42) !important;
        border-radius: 14px !important;
        padding: 18px !important;
        backdrop-filter: blur(14px) !important;
        box-shadow: 0 4px 25px rgba(0, 0, 0, 0.5) !important;
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
        background: rgba(7, 13, 19, 0.84);
        border: 1px solid rgba(0, 217, 217, 0.22);
        border-radius: 14px;
        padding: 26px 22px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        backdrop-filter: blur(14px);
    }
    .pricing-card-featured {
        background: linear-gradient(180deg, rgba(11, 23, 32, 0.92) 0%, rgba(5, 9, 13, 0.92) 100%);
        border: 2px solid #00D9D9;
        box-shadow: 0 8px 32px rgba(0, 217, 217, 0.25);
        border-radius: 14px;
        padding: 26px 22px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        backdrop-filter: blur(16px);
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

def exibir_tabela_precos():
    st.markdown("### 💎 Planos de Acompanhamento Mensal")
    st.markdown("Disponibilizamos planos para **empresas** e versões personalizadas para **gabinetes de contabilidade**:")
    
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
                    <li><span class="check-icon">✓</span> Leitura e visualização do SAF-T</li>
                    <li><span class="check-icon">✓</span> KPIs essenciais de faturação</li>
                    <li><span class="check-icon">✓</span> Curva ABC e Alertas de Risco</li>
                    <li><span class="check-icon">✓</span> Relatório de 1 página</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.button("Plano Ativo no Ecrã", disabled=True, key="btn_free_tab")

    with col_p2:
        st.markdown("""
        <div class="pricing-card">
            <div>
                <span class="badge-pill badge-turquoise">Empresas</span>
                <h3 style="margin: 0; color: #ffffff;">PME Gestão</h3>
                <div class="pricing-price">29 € <span style="font-size: 15px; color: #94a3b8; font-weight: normal;">/mês</span></div>
                <div class="pricing-sub">Acompanhamento executivo contínuo</div>
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
    <span class="badge-pill badge-turquoise">⚡ PLATAFORMA CORPORATIVA • SAF-T ANALYTICS</span>
    <h1 style="margin: 0; font-size: 2.3rem; font-weight: 800; color: #ffffff;">SAF-T Intelligence Pro</h1>
    <h3 style="margin: 4px 0 0 0; font-size: 1.15rem; font-weight: 600; color: #00D9D9;">Diagnóstico e Auditoria Executiva para PMEs e Contabilidade</h3>
    <p style="margin: 8px 0 0 0; color: #94a3b8; font-size: 0.95rem;">
        Processamento seguro de ficheiros fiscais, apuramento de volume real sem notas de crédito, matriz 80/20 e conferência de IVA.
    </p>
</div>
""", unsafe_allow_html=True)

ficheiro_saft = st.file_uploader("📂 Arraste ou selecione o ficheiro SAF-T (.xml) da empresa", type=["xml"])

# ---------------- CASO 1: PÁGINA INICIAL CORPORATIVA ----------------
if ficheiro_saft is None:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Pilares de Inteligência Financeira e Fiscal:")
    col_h1, col_h2, col_h3 = st.columns(3)

    with col_h1:
        st.markdown("""
        <div class="glass-card">
            <span class="badge-pill badge-turquoise">Segurança Corporativa</span>
            <h3 style="margin-top: 8px; color: #ffffff;">🔒 100% In-Memory (RGPD)</h3>
            <p style="color: #94a3b8; font-size: 14px; margin-top: 6px;">
                Os dados fiscais e documentos são analisados estritamente na memória da sessão de navegação. Nenhum valor comercial é gravado em bases de dados externas.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_h2:
        st.markdown("""
        <div class="glass-card">
            <span class="badge-pill badge-turquoise">Gestão Estratégica</span>
            <h3 style="margin-top: 8px; color: #ffffff;">📊 Curva ABC & Risco 80/20</h3>
            <p style="color: #94a3b8; font-size: 14px; margin-top: 6px;">
                Identifica os clientes críticos que asseguram 80% do fluxo de caixa e obtém alertas automáticos sobre dependência excessiva de faturação.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_h3:
        st.markdown("""
        <div class="glass-card">
            <span class="badge-pill badge-turquoise">Conferência Fiscal</span>
            <h3 style="margin-top: 8px; color: #ffffff;">⚖️ Auditoria de IVA</h3>
            <p style="color: #94a3b8; font-size: 14px; margin-top: 6px;">
                Resumo instantâneo de faturas emitidas vs. notas de crédito, discriminado por escalões de imposto (Normal 23%, Intermédia, Reduzida e Isenções).
            </p>
        </div>
        """, unsafe_allow_html=True)

# ---------------- CASO 2: PROCESSAMENTO E PAINEL EXECUTIVO ----------------
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

        # TAB 1: VISÃO GERAL
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
                    st.error(f"🚨 **Dependência Crítica de Carteira:** O cliente líder gera **{concentracao_top1:.1f}%** de toda a receita. Risco elevado para a sustentabilidade da tesouraria.")
                elif concentracao_top1 > 25:
                    st.warning(f"⚠️ **Atenção à Concentração:** O principal cliente representa **{concentracao_top1:.1f}%** do volume de negócios.")
                else:
                    st.success(f"✅ **Carteira Saudável:** A receita está bem distribuída. O cliente líder pesa apenas **{concentracao_top1:.1f}%**.")

            with d_col2:
                if taxa_nc > 5:
                    st.error(f"🚨 **Taxa de Anulação Alta ({taxa_nc:.1f}%):** As notas de crédito superam os padrões saudáveis (>5%). Indicador de possíveis falhas na faturação ou devoluções de serviço.")
                else:
                    st.success(f"✅ **Operação Eficiente:** Taxa de notas de crédito reduzida ({taxa_nc:.1f}%), dentro dos parâmetros ótimos.")

            st.markdown("---")
            st.markdown("#### Ritmo Diário de Vendas no Período")
            df['Data_dt'] = pd.to_datetime(df['Data'], errors='coerce')
            df_diario = df.groupby(df['Data_dt'].dt.date)['ValorBruto'].sum().reset_index()
            df_diario.columns = ['Data', 'Faturação Diária (€)']
            st.line_chart(df_diario.set_index('Data'), color="#00D9D9")

        # TAB 2: CURVA ABC
        with tab_abc:
            st.markdown("#### Segmentação Estratégica de Carteira (Regra 80/20)")
            st.caption("Classificação automática dos clientes que asseguram o volume financeiro da empresa.")

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
                st.bar_chart(df_abc.head(10).set_index('Cliente')['ValorBruto'], horizontal=True, color="#00D9D9")

            with col_abc_table:
                st.subheader("Detetor Estratégico")
                df_exibicao = df_abc[['Cliente', 'ValorBruto', '% Receita', 'Categoria ABC']].copy()
                df_exibicao['ValorBruto'] = df_exibicao['ValorBruto'].map("{:,.2f} €".format)
                df_exibicao['% Receita'] = df_exibicao['% Receita'].map("{:.2f}%".format)
                st.dataframe(df_exibicao, use_container_width=True, hide_index=True)

        # TAB 3: AUDITORIA DE IVA
        with tab_iva:
            st.markdown("#### Resumo Fiscal de IVA Liquidado")
            st.caption("Conferência automática por escalão tributável para gabinetes de contabilidade e gestores.")

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

        # TAB 4: PLANOS & RELATÓRIO
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
        st.error(f"Erro ao processar ficheiro SAF-T: {e}")
