import streamlit as st
import streamlit.components.v1 as components
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
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 24px;
        margin-bottom: 20px;
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

    .hero-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 24px;
        height: 100%;
    }

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

# ---------------- COMPONENTE 3D AWWWARDS: THE STATE OF THE GALLERY ----------------
def render_3d_gallery_transition():
    gallery_3d_code = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            * { box-sizing: border-box; }
            body { margin: 0; padding: 0; overflow: hidden; background: #07090e; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
            #scene-wrap {
                width: 100%;
                height: 420px;
                position: relative;
                border-radius: 16px;
                background: radial-gradient(circle at 50% 30%, #172554 0%, #07090e 75%);
                border: 1px solid #1e293b;
                overflow: hidden;
                box-shadow: inset 0 0 80px rgba(0,0,0,0.8);
            }
            .hud-header {
                position: absolute;
                top: 16px;
                left: 20px;
                right: 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                pointer-events: none;
                z-index: 10;
            }
            .hud-badge {
                font-size: 11px;
                font-weight: 700;
                color: #38bdf8;
                letter-spacing: 1.5px;
                text-transform: uppercase;
                background: rgba(15, 23, 42, 0.75);
                border: 1px solid rgba(56, 189, 248, 0.35);
                padding: 6px 14px;
                border-radius: 20px;
                backdrop-filter: blur(8px);
            }
            .hud-status {
                font-size: 11px;
                color: #94a3b8;
                letter-spacing: 1px;
                background: rgba(15, 23, 42, 0.6);
                padding: 6px 12px;
                border-radius: 20px;
                border: 1px solid rgba(255,255,255,0.08);
            }
            /* Botões de Transição de Cena (Estilo Awwwards) */
            .scene-nav {
                position: absolute;
                bottom: 18px;
                left: 50%;
                transform: translateX(-50%);
                display: flex;
                gap: 8px;
                background: rgba(15, 23, 42, 0.85);
                border: 1px solid #334155;
                padding: 5px 8px;
                border-radius: 30px;
                backdrop-filter: blur(12px);
                z-index: 10;
            }
            .scene-btn {
                background: transparent;
                border: none;
                color: #94a3b8;
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 0.8px;
                padding: 8px 14px;
                border-radius: 20px;
                cursor: pointer;
                transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            }
            .scene-btn:hover {
                color: #f8fafc;
                background: rgba(255,255,255,0.06);
            }
            .scene-btn.active {
                background: #0284c7;
                color: #ffffff;
                box-shadow: 0 0 16px rgba(56, 189, 248, 0.4);
            }
            canvas { display: block; width: 100%; height: 100%; cursor: grab; }
            canvas:active { cursor: grabbing; }
        </style>
    </head>
    <body>
        <div id="scene-wrap">
            <div class="hud-header">
                <div class="hud-badge">● THE STATE OF THE GALLERY // 3D SCENE TRANSITION</div>
                <div class="hud-status" id="hud-indicator">CENA 01 / 03 • MODO TÚNEL</div>
            </div>

            <div class="scene-nav">
                <button class="scene-btn active" id="btn-0" onclick="triggerScene(0)">01 // TÚNEL PERSPECTIVA</button>
                <button class="scene-btn" id="btn-1" onclick="triggerScene(1)">02 // SPOTLIGHT FOCUS</button>
                <button class="scene-btn" id="btn-2" onclick="triggerScene(2)">03 // MATRIZ 3D</button>
            </div>

            <canvas id="stage"></canvas>
        </div>

        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>

        <script>
            const container = document.getElementById('scene-wrap');
            const canvas = document.getElementById('stage');
            const hudIndicator = document.getElementById('hud-indicator');

            // 1. Criação da Cena e Câmara
            const scene = new THREE.Scene();
            scene.fog = new THREE.FogExp2(0x07090e, 0.055);

            const camera = new THREE.PerspectiveCamera(46, container.clientWidth / container.clientHeight, 0.1, 100);
            camera.position.set(0, 0, 7.5);

            const renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true });
            renderer.setSize(container.clientWidth, container.clientHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

            // 2. Partículas Cósmicas / Luzes no Espaço
            const pCount = 280;
            const pGeo = new THREE.BufferGeometry();
            const pPos = new Float32Array(pCount * 3);
            for(let i = 0; i < pCount * 3; i += 3) {
                pPos[i] = (Math.random() - 0.5) * 22;
                pPos[i+1] = (Math.random() - 0.5) * 14;
                pPos[i+2] = (Math.random() - 0.5) * 16;
            }
            pGeo.setAttribute('position', new THREE.BufferAttribute(pPos, 3));
            const pMat = new THREE.PointsMaterial({
                color: 0x38bdf8,
                size: 0.05,
                transparent: true,
                opacity: 0.75
            });
            const particles = new THREE.Points(pGeo, pMat);
            scene.add(particles);

            // 3. Gerador Dinâmico de Texturas de Cartões (Dark Glass UI)
            function makeCardCanvas(badge, title, mainVal, subText, visualType) {
                const cv = document.createElement('canvas');
                cv.width = 512;
                cv.height = 320;
                const ctx = cv.getContext('2d');

                // Fundo gradiente escuro de luxo
                const bgGrad = ctx.createLinearGradient(0, 0, 512, 320);
                bgGrad.addColorStop(0, '#0f172a');
                bgGrad.addColorStop(1, '#020617');
                ctx.fillStyle = bgGrad;
                ctx.fillRect(0, 0, 512, 320);

                // Moldura brilhante
                ctx.strokeStyle = '#38bdf8';
                ctx.lineWidth = 4;
                ctx.strokeRect(3, 3, 506, 314);

                // Badge no topo
                ctx.fillStyle = 'rgba(56, 189, 248, 0.16)';
                ctx.fillRect(28, 24, 180, 32);
                ctx.strokeStyle = 'rgba(56, 189, 248, 0.4)';
                ctx.lineWidth = 1.5;
                ctx.strokeRect(28, 24, 180, 32);

                ctx.fillStyle = '#38bdf8';
                ctx.font = 'bold 12px -apple-system, sans-serif';
                ctx.fillText(badge, 40, 45);

                // Título
                ctx.fillStyle = '#94a3b8';
                ctx.font = '14px -apple-system, sans-serif';
                ctx.fillText(title, 28, 92);

                // Valor Principal em Destaque
                ctx.fillStyle = '#f8fafc';
                ctx.font = 'bold 36px -apple-system, sans-serif';
                ctx.fillText(mainVal, 28, 140);

                // Subtítulo
                ctx.fillStyle = '#38bdf8';
                ctx.font = '13px -apple-system, sans-serif';
                ctx.fillText(subText, 28, 172);

                // Gráfico embutido no cartão
                if(visualType === 'curve') {
                    ctx.strokeStyle = '#38bdf8';
                    ctx.lineWidth = 3;
                    ctx.beginPath();
                    ctx.moveTo(28, 260);
                    ctx.bezierCurveTo(140, 290, 220, 205, 330, 240);
                    ctx.bezierCurveTo(390, 255, 430, 190, 484, 195);
                    ctx.stroke();

                    ctx.lineTo(484, 295);
                    ctx.lineTo(28, 295);
                    ctx.fillStyle = 'rgba(56, 189, 248, 0.09)';
                    ctx.fill();
                } else if(visualType === 'pareto') {
                    const bars = [0.85, 0.58, 0.32, 0.18];
                    const colors = ['#38bdf8', '#818cf8', '#c084fc', '#64748b'];
                    bars.forEach((b, idx) => {
                        ctx.fillStyle = colors[idx];
                        ctx.fillRect(28 + idx * 56, 290 - b * 90, 40, b * 90);
                    });
                } else if(visualType === 'donut') {
                    ctx.strokeStyle = 'rgba(56, 189, 248, 0.2)';
                    ctx.lineWidth = 12;
                    ctx.beginPath();
                    ctx.arc(420, 230, 42, 0, Math.PI * 2);
                    ctx.stroke();

                    ctx.strokeStyle = '#a855f7';
                    ctx.lineWidth = 12;
                    ctx.beginPath();
                    ctx.arc(420, 230, 42, -Math.PI / 2, Math.PI * 0.9);
                    ctx.stroke();
                } else if(visualType === 'wave') {
                    ctx.strokeStyle = '#22c55e';
                    ctx.lineWidth = 3;
                    ctx.beginPath();
                    ctx.moveTo(28, 250);
                    ctx.lineTo(140, 250);
                    ctx.lineTo(170, 200);
                    ctx.lineTo(210, 280);
                    ctx.lineTo(250, 225);
                    ctx.lineTo(290, 250);
                    ctx.lineTo(484, 250);
                    ctx.stroke();
                } else {
                    ctx.fillStyle = 'rgba(148, 163, 184, 0.2)';
                    for(let r = 0; r < 3; r++) {
                        ctx.fillRect(28, 215 + r * 25, 456, 12);
                    }
                }

                const tex = new THREE.CanvasTexture(cv);
                tex.generateMipmaps = true;
                return tex;
            }

            // 4. Criação dos 5 Cartões 3D
            const cardData = [
                { badge: "FATURAÇÃO LÍQUIDA", title: "Ritmo de Receita Diário", val: "650.420 €", sub: "+18.4% vs mês homólogo", type: "curve" },
                { badge: "CURVA ABC // 80-20", title: "Concentração Estratégica", val: "3 Clientes Top", sub: "78.4% do volume de negócios", type: "pareto" },
                { badge: "AUDITORIA FISCAL", title: "Apuramento por Taxa", val: "23% • 13% • 6%", sub: "Conferência automática de IVA", type: "donut" },
                { badge: "QUALIDADE OPERACIONAL", title: "Taxa de Devoluções (NC)", val: "2.1% Anulado", sub: "Dentro dos padrões ótimos", type: "wave" },
                { badge: "RELATÓRIO EXECUTIVO", title: "Diagnóstico para Decisores", val: "1-Click PDF", sub: "Pronto para apresentar à gerência", type: "doc" }
            ];

            const cards = [];
            const cardGeo = new THREE.PlaneGeometry(3.0, 1.85);

            cardData.forEach((d, i) => {
                const group = new THREE.Group();

                // Cartão frontal
                const matFront = new THREE.MeshBasicMaterial({
                    map: makeCardCanvas(d.badge, d.title, d.val, d.sub, d.type),
                    transparent: true,
                    opacity: 0.96,
                    side: THREE.DoubleSide
                });
                const meshFront = new THREE.Mesh(cardGeo, matFront);
                group.add(meshFront);

                // Placa traseira em vidro escuro
                const matBack = new THREE.MeshBasicMaterial({
                    color: 0x070d1a,
                    transparent: true,
                    opacity: 0.85,
                    side: THREE.DoubleSide
                });
                const meshBack = new THREE.Mesh(cardGeo, matBack);
                meshBack.position.z = -0.02;
                group.add(meshBack);

                // Bordas luminosas com EdgesGeometry
                const edges = new THREE.EdgesGeometry(cardGeo);
                const line = new THREE.LineSegments(
                    edges, 
                    new THREE.LineBasicMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.65 })
                );
                group.add(line);

                scene.add(group);
                cards.push(group);
            });

            // 5. Configuração das 3 Cenas (Awwwards Scene Layouts)
            const sceneLayouts = [
                // CENA 0: TÚNEL PERSPECTIVA (O visual icónico de 'The State of the Gallery')
                {
                    name: "CENA 01 / 03 • MODO TÚNEL",
                    camPos: [0, 0, 7.5],
                    cards: [
                        { pos: [-4.2, 0.5, -0.2], rot: [0.08, 0.45, -0.05] },
                        { pos: [-2.1, -0.3, 1.4], rot: [0.04, 0.25, -0.02] },
                        { pos: [0.2, 0.3, 2.5], rot: [-0.04, -0.06, 0.01] }, // Centro em destaque
                        { pos: [2.5, -0.3, 1.2], rot: [0.03, -0.32, 0.02] },
                        { pos: [4.6, 0.5, -0.4], rot: [0.07, -0.52, 0.06] }
                    ]
                },
                // CENA 1: SPOTLIGHT DEEP FOCUS (Voo da câmara em direção ao núcleo)
                {
                    name: "CENA 02 / 03 • SPOTLIGHT FOCUS",
                    camPos: [0, 0.2, 5.2],
                    cards: [
                        { pos: [-4.8, 2.2, -2.0], rot: [0.25, 0.45, -0.1] },
                        { pos: [-4.2, -2.0, -1.5], rot: [-0.2, 0.35, 0.1] },
                        { pos: [0.0, 0.0, 2.8], rot: [0.0, 0.0, 0.0] }, // Em plano direto na lente
                        { pos: [4.2, -2.0, -1.5], rot: [-0.2, -0.35, -0.1] },
                        { pos: [4.8, 2.2, -2.0], rot: [0.25, -0.45, 0.1] }
                    ]
                },
                // CENA 2: MATRIZ HOLO-DECK 3D (Vista arquitetural isométrica)
                {
                    name: "CENA 03 / 03 • MATRIZ 3D",
                    camPos: [0, 2.8, 6.6],
                    cards: [
                        { pos: [-3.4, 1.4, 0.6], rot: [-0.38, 0.24, 0.06] },
                        { pos: [0.0, 1.4, 0.6], rot: [-0.38, 0.0, 0.0] },
                        { pos: [3.4, 1.4, 0.6], rot: [-0.38, -0.24, -0.06] },
                        { pos: [-1.8, -1.3, 1.5], rot: [-0.38, 0.12, 0.03] },
                        { pos: [1.8, -1.3, 1.5], rot: [-0.38, -0.12, -0.03] }
                    ]
                }
            ];

            let activeSceneIdx = 0;

            // Função principal de Transição Cinematográfica com GSAP
            function triggerScene(index) {
                activeSceneIdx = index;
                const layout = sceneLayouts[index];

                hudIndicator.innerText = layout.name;

                // Atualizar estilo visual dos botões
                for(let b = 0; b < 3; b++) {
                    const btn = document.getElementById('btn-' + b);
                    if(b === index) btn.classList.add('active');
                    else btn.classList.remove('active');
                }

                // Efeito Warp nas partículas
                gsap.to(particles.rotation, {
                    y: particles.rotation.y + Math.PI * 0.45,
                    duration: 1.4,
                    ease: "power2.inOut"
                });

                // Transição da Câmara
                gsap.to(camera.position, {
                    x: layout.camPos[0],
                    y: layout.camPos[1],
                    z: layout.camPos[2],
                    duration: 1.5,
                    ease: "power3.inOut"
                });

                // Animação individual dos cartões com efeito dominó (Stagger)
                cards.forEach((card, i) => {
                    const target = layout.cards[i];

                    gsap.to(card.position, {
                        x: target.pos[0],
                        y: target.pos[1],
                        z: target.pos[2],
                        duration: 1.4,
                        delay: i * 0.045,
                        ease: "power3.inOut"
                    });

                    gsap.to(card.rotation, {
                        x: target.rot[0],
                        y: target.rot[1],
                        z: target.rot[2],
                        duration: 1.4,
                        delay: i * 0.045,
                        ease: "power3.inOut"
                    });
                });
            }

            // Iniciar com a Cena 0
            triggerScene(0);

            // 6. Transição Automática a cada 6 segundos
            let autoCycleTimer = setInterval(() => {
                let next = (activeSceneIdx + 1) % 3;
                triggerScene(next);
            }, 6000);

            // Ao clicar num botão, pausar o timer automático
            window.triggerScene = function(idx) {
                clearInterval(autoCycleTimer);
                triggerScene(idx);
                // Reiniciar o ciclo 10 segundos após interação manual
                autoCycleTimer = setInterval(() => {
                    let next = (activeSceneIdx + 1) % 3;
                    triggerScene(next);
                }, 7500);
            };

            // 7. Parallax Interativo com o Rato
            let mouseX = 0, mouseY = 0;
            let targetCamX = 0, targetCamY = 0;

            window.addEventListener('mousemove', (e) => {
                const rect = container.getBoundingClientRect();
                mouseX = ((e.clientX - rect.left) / container.clientWidth - 0.5) * 2;
                mouseY = -((e.clientY - rect.top) / container.clientHeight - 0.5) * 2;
            });

            // 8. Loop de Renderização a 60 FPS
            function render() {
                requestAnimationFrame(render);

                // Flutuação subtil contínua das partículas
                particles.rotation.y += 0.0008;

                // Amortecimento físico no movimento da câmara (Lerp)
                const baseCam = sceneLayouts[activeSceneIdx].camPos;
                targetCamX = baseCam[0] + mouseX * 0.65;
                targetCamY = baseCam[1] + mouseY * 0.45;

                camera.position.x += (targetCamX - camera.position.x) * 0.05;
                camera.position.y += (targetCamY - camera.position.y) * 0.05;
                camera.lookAt(0, 0, 0);

                renderer.render(scene, camera);
            }
            render();

            // Responsividade no redimensionamento
            window.addEventListener('resize', () => {
                camera.aspect = container.clientWidth / container.clientHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(container.clientWidth, container.clientHeight);
            });
        </script>
    </body>
    </html>
    """
    components.html(gallery_3d_code, height=435)

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
    st.markdown("Gostou do diagnóstico? Disponibilizamos acompanhamento contínuo para a sua empresa ou para toda a carteira do seu gabinete:")
    
    col_p1, col_p2, col_p3 = st.columns(3)

    with col_p1:
        st.markdown("""
        <div class="pricing-card">
            <div>
                <span class="badge-pill badge-blue">Diagnóstico</span>
                <h3 style="margin: 0; color: #f8fafc;">Acesso Gratuito</h3>
                <div class="pricing-price">0 €</div>
                <div class="pricing-sub">Para testes individuais pontuais</div>
                <ul class="feature-list">
                    <li><span class="check-icon">✓</span> Leitura e visualização do SAF-T</li>
                    <li><span class="check-icon">✓</span> KPIs essenciais de faturação</li>
                    <li><span class="check-icon">✓</span> Curva ABC e Alertas no ecrã</li>
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
                <span class="badge-pill badge-green">Empresas</span>
                <h3 style="margin: 0; color: #f8fafc;">PME Gestão</h3>
                <div class="pricing-price">29 € <span style="font-size: 15px; color: #94a3b8; font-weight: normal;">/mês</span></div>
                <div class="pricing-sub">Acompanhamento executivo mensal</div>
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
                <h3 style="margin: 0; color: #f8fafc;">Gabinete Pro</h3>
                <div class="pricing-price">79 € <span style="font-size: 15px; color: #38bdf8; font-weight: normal;">/mês</span></div>
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

# ---------------- CABEÇALHO PRINCIPAL ----------------
st.markdown("""
<div class="main-header">
    <span class="badge-pill badge-blue">SAF-T Executive Analytics v3.0</span>
    <h1 style="margin: 0; font-size: 28px; color: #f8fafc;">⚡ Plataforma de Inteligência e Auditoria SAF-T</h1>
    <p style="margin: 6px 0 0 0; color: #94a3b8; font-size: 15px;">
        Transforme ficheiros fiscais mensais num diagnóstico executivo de faturação, dependência de clientes e IVA.
    </p>
</div>
""", unsafe_allow_html=True)

ficheiro_saft = st.file_uploader("📂 Arraste ou selecione o ficheiro SAF-T (.xml) da empresa", type=["xml"])

# ---------------- CASO 1: PÁGINA INICIAL COM O MOTOR 3D THE STATE OF THE GALLERY ----------------
if ficheiro_saft is None:
    # GALERIA 3D COM TRANSIÇÃO DE CENA DA AWWWARDS
    render_3d_gallery_transition()

    st.markdown("### Diagnóstico financeiro instantâneo em 3 pilares:")
    col_h1, col_h2, col_h3 = st.columns(3)

    with col_h1:
        st.markdown("""
        <div class="hero-card">
            <span class="badge-pill badge-green">Segurança Máxima</span>
            <h3 style="margin-top: 5px; color: #f8fafc;">🔒 100% Confidencial</h3>
            <p style="color: #94a3b8; font-size: 14px;">
                Os ficheiros são processados exclusivamente na memória volátil durante a sessão. Nenhum dado fiscal, cliente ou valor é gravado em servidores ou bases de dados externas.
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

    st.info("👆 **Comece já:** Selecione ou arraste um ficheiro SAF-T (.xml) acima para ver o diagnóstico completo.")

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

        # TAB 2: CURVA ABC
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

        # TAB 3: AUDITORIA DE IVA
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
