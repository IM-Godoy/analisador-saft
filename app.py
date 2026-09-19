import streamlit as st
import streamlit.components.v1 as components
import xml.etree.ElementTree as ET
import pandas as pd
import urllib.parse
import urllib.request
import json

st.set_page_config(
    page_title="Analisador SAF-T | Igor - Junior Data Analyst", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- ESTILOS VISUAIS TEMA TURQUESA & DARK ----------------
st.markdown("""
    <style>
    /* Fundo Global e Tipografia */
    .stApp {
        background-color: #06090c;
        color: #f1f5f9;
        font-family: 'Poppins', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Cabeçalho Executivo */
    .main-header {
        background: linear-gradient(135deg, #091319 0%, #06090c 100%);
        border: 1px solid rgba(0, 217, 217, 0.25);
        border-radius: 14px;
        padding: 24px;
        margin-bottom: 25px;
        box-shadow: 0 4px 25px rgba(0, 0, 0, 0.5);
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
        background: rgba(0, 217, 217, 0.12); 
        color: #00D9D9; 
        border: 1px solid rgba(0, 217, 217, 0.35); 
    }
    .badge-amber { 
        background: rgba(245, 158, 11, 0.15); 
        color: #f59e0b; 
        border: 1px solid rgba(245, 158, 11, 0.3); 
    }
    .badge-purple { 
        background: rgba(168, 85, 247, 0.15); 
        color: #c084fc; 
        border: 1px solid rgba(168, 85, 247, 0.3); 
    }

    /* Cartões de Métricas com Destaque Turquesa */
    div[data-testid="stMetric"] {
        background-color: #0a1117;
        border: 1px solid rgba(0, 217, 217, 0.2);
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
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
        text-shadow: 0 0 15px rgba(0, 217, 217, 0.25);
    }

    .hero-card {
        background: #0a1117;
        border: 1px solid rgba(0, 217, 217, 0.2);
        border-radius: 14px;
        padding: 24px;
        height: 100%;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }

    /* Cartões de Planos / Preços */
    .pricing-card {
        background: #0a1117;
        border: 1px solid rgba(0, 217, 217, 0.2);
        border-radius: 14px;
        padding: 26px 22px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .pricing-card-featured {
        background: linear-gradient(180deg, #0d1a24 0%, #06090c 100%);
        border: 2px solid #00D9D9;
        box-shadow: 0 8px 30px rgba(0, 217, 217, 0.25);
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

# ---------------- HERO / LANDING PAGE 3D (AWWWARDS TURQUOISE ENGINE) ----------------
def render_3d_hero_section():
    landing_3d_html = """
    <!DOCTYPE html>
    <html lang="pt">
    <head>
        <meta charset="UTF-8">
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
            :root {
                --primary: #00D9D9;
                --primary-dark: #00A8A8;
                --primary-glow: rgba(0, 217, 217, 0.45);
                --bg-deep: #06090c;
                --bg-card: rgba(10, 17, 23, 0.72);
                --border-glass: rgba(0, 217, 217, 0.25);
                --text-main: #f1f5f9;
                --text-muted: #94a3b8;
                --font-main: 'Poppins', -apple-system, sans-serif;
            }
            body {
                width: 100%;
                height: 590px;
                overflow: hidden;
                background-color: var(--bg-deep);
                color: var(--text-main);
                font-family: var(--font-main);
                position: relative;
                border-radius: 16px;
                border: 1px solid var(--border-glass);
            }
            #webgl-canvas {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 1;
                cursor: grab;
            }
            #webgl-canvas:active { cursor: grabbing; }

            .ui-layer {
                position: relative;
                z-index: 2;
                width: 100%;
                height: 100%;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                padding: 24px 30px;
                pointer-events: none;
            }
            .interactive { pointer-events: auto; }

            header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                width: 100%;
            }
            .brand-badge {
                display: flex;
                align-items: center;
                gap: 10px;
                background: var(--bg-card);
                border: 1px solid var(--border-glass);
                padding: 7px 16px;
                border-radius: 40px;
                backdrop-filter: blur(12px);
            }
            .status-dot {
                width: 8px;
                height: 8px;
                background-color: var(--primary);
                border-radius: 50%;
                box-shadow: 0 0 10px var(--primary);
                animation: pulseGlow 2s infinite ease-in-out;
            }
            .brand-text {
                font-size: 0.78rem;
                font-weight: 700;
                letter-spacing: 1.2px;
                text-transform: uppercase;
                color: var(--primary);
            }
            .location-badge {
                background: var(--bg-card);
                border: 1px solid rgba(255, 255, 255, 0.08);
                padding: 7px 16px;
                border-radius: 40px;
                font-size: 0.8rem;
                color: var(--text-muted);
                backdrop-filter: blur(12px);
            }
            .location-badge span { color: var(--primary); }

            .hero-container {
                max-width: 820px;
                margin-top: auto;
                margin-bottom: auto;
            }
            .tag-pill {
                display: inline-flex;
                align-items: center;
                background: rgba(0, 217, 217, 0.1);
                border: 1px solid var(--border-glass);
                color: var(--primary);
                padding: 5px 14px;
                border-radius: 20px;
                font-size: 0.75rem;
                font-weight: 600;
                letter-spacing: 0.5px;
                text-transform: uppercase;
                margin-bottom: 12px;
                backdrop-filter: blur(8px);
            }
            h1.hero-title {
                font-size: 3.2rem;
                font-weight: 800;
                line-height: 1.05;
                letter-spacing: -1.2px;
                margin-bottom: 8px;
                background: linear-gradient(135deg, #ffffff 40%, var(--primary) 95%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-shadow: 0 10px 40px rgba(0, 217, 217, 0.15);
            }
            h2.hero-subtitle {
                font-size: 1.35rem;
                font-weight: 600;
                color: var(--primary);
                margin-bottom: 12px;
            }
            p.hero-description {
                font-size: 0.95rem;
                line-height: 1.55;
                color: var(--text-muted);
                max-width: 650px;
                margin-bottom: 24px;
            }
            .author-tag {
                color: #ffffff;
                font-weight: 600;
                border-bottom: 1px dashed var(--primary);
                padding-bottom: 2px;
            }

            .cta-group {
                display: flex;
                flex-wrap: wrap;
                gap: 14px;
                align-items: center;
            }
            .btn {
                position: relative;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                padding: 12px 26px;
                border-radius: 10px;
                font-size: 0.88rem;
                font-weight: 600;
                text-decoration: none;
                cursor: pointer;
                transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            }
            .btn-primary {
                background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
                color: #031317;
                box-shadow: 0 0 20px var(--primary-glow);
                border: 1px solid var(--primary);
            }
            .btn-primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 0 30px rgba(0, 217, 217, 0.7);
                color: #000;
            }
            .btn-secondary {
                background: var(--bg-card);
                color: var(--text-main);
                border: 1px solid var(--border-glass);
                backdrop-filter: blur(14px);
            }
            .btn-secondary:hover {
                transform: translateY(-2px);
                background: rgba(0, 217, 217, 0.12);
                border-color: var(--primary);
                color: #ffffff;
            }

            footer {
                display: flex;
                justify-content: space-between;
                align-items: flex-end;
                width: 100%;
            }
            .scene-selector {
                display: flex;
                gap: 6px;
                background: var(--bg-card);
                border: 1px solid var(--border-glass);
                padding: 5px 8px;
                border-radius: 30px;
                backdrop-filter: blur(16px);
            }
            .scene-btn {
                background: transparent;
                border: none;
                color: var(--text-muted);
                font-size: 0.72rem;
                font-weight: 700;
                padding: 6px 14px;
                border-radius: 20px;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .scene-btn:hover { color: #fff; }
            .scene-btn.active {
                background: var(--primary);
                color: #041014;
                box-shadow: 0 0 12px var(--primary-glow);
            }
            .telemetry-tag {
                font-size: 0.72rem;
                color: #64748b;
                letter-spacing: 0.8px;
            }

            @keyframes pulseGlow {
                0%, 100% { opacity: 1; transform: scale(1); }
                50% { opacity: 0.4; transform: scale(0.85); }
            }
            @media (max-width: 768px) {
                h1.hero-title { font-size: 2.2rem; }
                .location-badge, .telemetry-tag { display: none; }
                .scene-selector { width: 100%; justify-content: center; }
            }
        </style>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap" rel="stylesheet">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
    </head>
    <body>
        <canvas id="webgl-canvas"></canvas>

        <div class="ui-layer">
            <header>
                <div class="brand-badge interactive">
                    <div class="status-dot"></div>
                    <div class="brand-text">SAF-T Intelligence 3D</div>
                </div>
                <div class="location-badge interactive">
                    <span>📍</span> Aveiro, Portugal
                </div>
            </header>

            <main class="hero-container">
                <div class="tag-pill interactive">
                    ⚡ Nova Dimensão em Auditoria Fiscal
                </div>
                <h1 class="hero-title">Analisador SAF-T</h1>
                <h2 class="hero-subtitle">Análise de Ficheiros SAF-T Simplificada</h2>
                <p class="hero-description">
                    Importa, processa e analisa dados SAF-T com precisão | 
                    <span class="author-tag">Igor - Junior Data Analyst</span>. 
                    Visualização de faturação em tempo real, curva de concentração 80/20 e mapa fiscal de IVA.
                </p>

                <div class="cta-group">
                    <a href="https://im-godoy-analisador-saft-app-xwvmax.streamlit.app/" target="_top" class="btn btn-primary interactive" id="cta-analyze">
                        <span>Iniciar Análise</span>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg>
                    </a>

                    <a href="https://github.com/IM-Godoy/analisador-saft" target="_blank" class="btn btn-secondary interactive">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/></svg>
                        <span>Ver Código</span>
                    </a>

                    <a href="https://www.linkedin.com/in/im-godoy/" target="_blank" class="btn btn-secondary interactive" title="LinkedIn">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/></svg>
                        <span>LinkedIn</span>
                    </a>
                </div>
            </main>

            <footer>
                <div class="telemetry-tag">TURQUOISE WEBGL ENGINE // 60 FPS</div>
                <div class="scene-selector interactive">
                    <button class="scene-btn active" id="btn-scene-0" onclick="setScene(0)">01 // TÚNEL ESPIRAL</button>
                    <button class="scene-btn" id="btn-scene-1" onclick="setScene(1)">02 // VÓRTICE WARP</button>
                    <button class="scene-btn" id="btn-scene-2" onclick="setScene(2)">03 // MATRIZ DATA-CORE</button>
                </div>
            </footer>
        </div>

        <script>
            const canvas = document.getElementById('webgl-canvas');
            const scene = new THREE.Scene();
            scene.fog = new THREE.FogExp2(0x06090c, 0.045);

            const camera = new THREE.PerspectiveCamera(52, window.innerWidth / window.innerHeight, 0.1, 100);
            camera.position.set(0, 0, 6.8);

            const renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

            // Partículas Turquesa em Vórtice
            const pCount = 1200;
            const pGeo = new THREE.BufferGeometry();
            const pPos = new Float32Array(pCount * 3);
            const pSpeeds = new Float32Array(pCount);

            for (let i = 0; i < pCount * 3; i += 3) {
                const angle = Math.random() * Math.PI * 2;
                const radius = 2.0 + Math.random() * 6.0;
                pPos[i] = Math.cos(angle) * radius;
                pPos[i + 1] = Math.sin(angle) * radius;
                pPos[i + 2] = (Math.random() - 0.5) * 45;
                pSpeeds[i / 3] = 0.04 + Math.random() * 0.08;
            }
            pGeo.setAttribute('position', new THREE.BufferAttribute(pPos, 3));

            const pMat = new THREE.PointsMaterial({
                color: 0x00D9D9,
                size: 0.045,
                transparent: true,
                opacity: 0.75,
                blending: THREE.AdditiveBlending
            });
            const particles = new THREE.Points(pGeo, pMat);
            scene.add(particles);

            // Anéis da Espiral / Túnel
            const ringsGroup = new THREE.Group();
            const ringGeo = new THREE.RingGeometry(3.1, 3.16, 8);
            const ringMat = new THREE.MeshBasicMaterial({
                color: 0x00A8A8,
                wireframe: true,
                transparent: true,
                opacity: 0.35,
                side: THREE.DoubleSide
            });

            for (let i = 0; i < 26; i++) {
                const ring = new THREE.Mesh(ringGeo, ringMat.clone());
                const zPos = -i * 1.5 + 4;
                const sAngle = i * 0.28;
                ring.position.set(Math.cos(sAngle) * 0.7, Math.sin(sAngle) * 0.7, zPos);
                ring.rotation.z = sAngle;
                ringsGroup.add(ring);
            }
            scene.add(ringsGroup);

            // Texturas Dinâmicas para os Cartões 3D
            function createCardTexture(title, val, sub) {
                const cv = document.createElement('canvas');
                cv.width = 512;
                cv.height = 280;
                const ctx = cv.getContext('2d');

                ctx.fillStyle = '#081017';
                ctx.fillRect(0, 0, 512, 280);

                ctx.strokeStyle = '#00D9D9';
                ctx.lineWidth = 6;
                ctx.strokeRect(3, 3, 506, 274);

                ctx.fillStyle = 'rgba(0, 217, 217, 0.15)';
                ctx.fillRect(28, 24, 180, 32);
                ctx.fillStyle = '#00D9D9';
                ctx.font = 'bold 13px Poppins, sans-serif';
                ctx.fillText("SAF-T AUDIT CORE", 38, 46);

                ctx.fillStyle = '#94a3b8';
                ctx.font = '16px Poppins, sans-serif';
                ctx.fillText(title, 28, 96);

                ctx.fillStyle = '#ffffff';
                ctx.font = 'bold 44px Poppins, sans-serif';
                ctx.fillText(val, 28, 155);

                ctx.fillStyle = '#00D9D9';
                ctx.font = '14px Poppins, sans-serif';
                ctx.fillText(sub, 28, 195);

                ctx.strokeStyle = '#00D9D9';
                ctx.lineWidth = 3;
                ctx.beginPath();
                ctx.moveTo(28, 235);
                ctx.bezierCurveTo(150, 260, 280, 200, 484, 215);
                ctx.stroke();

                return new THREE.CanvasTexture(cv);
            }

            const cardsData = [
                { t: "Faturação Líquida", v: "650.420 €", s: "Processamento XML instantâneo" },
                { t: "Curva ABC (Pareto)", v: "80% Receita", s: "Top 3 Clientes Críticos" },
                { t: "Auditoria Fiscal IVA", v: "23% • 13% • 6%", s: "Conferência automática por taxa" },
                { t: "Segurança de Dados", v: "100% In-Memory", s: "Sem gravação externa (RGPD)" }
            ];

            const cardsMeshes = [];
            const cardGeo = new THREE.PlaneGeometry(2.5, 1.4);

            cardsData.forEach((d, idx) => {
                const mat = new THREE.MeshBasicMaterial({
                    map: createCardTexture(d.t, d.v, d.s),
                    transparent: true,
                    opacity: 0.92,
                    side: THREE.DoubleSide
                });
                const mesh = new THREE.Mesh(cardGeo, mat);
                const prog = (idx / cardsData.length) * Math.PI * 2;
                mesh.position.set(Math.cos(prog) * 2.8, Math.sin(prog) * 1.5, -idx * 3.5 + 2);
                mesh.rotation.y = -Math.cos(prog) * 0.3;
                scene.add(mesh);
                cardsMeshes.push(mesh);
            });

            // 3 Cenas Awwwards
            const scenes = [
                { cam: { x: 0, y: 0, z: 6.8 }, rot: { x: 0, y: 0, z: 0 } },
                { cam: { x: 0, y: 0.4, z: 2.2 }, rot: { x: -0.15, y: 0.25, z: 0.1 } },
                { cam: { x: -1.8, y: 2.5, z: 4.8 }, rot: { x: -0.45, y: -0.3, z: -0.15 } }
            ];

            let activeScene = 0;
            function setScene(idx) {
                activeScene = idx;
                const target = scenes[idx];

                for (let i = 0; i < 3; i++) {
                    const btn = document.getElementById('btn-scene-' + i);
                    if (btn) {
                        if (i === idx) btn.classList.add('active');
                        else btn.classList.remove('active');
                    }
                }

                gsap.to(camera.position, {
                    x: target.cam.x, y: target.cam.y, z: target.cam.z,
                    duration: 1.8, ease: "power3.inOut"
                });
                gsap.to(camera.rotation, {
                    x: target.rot.x, y: target.rot.y, z: target.rot.z,
                    duration: 1.8, ease: "power3.inOut"
                });

                cardsMeshes.forEach((mesh, i) => {
                    gsap.to(mesh.rotation, {
                        z: mesh.rotation.z + Math.PI * 0.5,
                        duration: 1.4, delay: i * 0.05, ease: "power2.inOut"
                    });
                });
            }

            let autoTimer = setInterval(() => {
                setScene((activeScene + 1) % 3);
            }, 8000);

            window.setScene = function(idx) {
                clearInterval(autoTimer);
                setScene(idx);
                autoTimer = setInterval(() => {
                    setScene((activeScene + 1) % 3);
                }, 10000);
            };

            // Parallax Rato
            let mouseX = 0, mouseY = 0, tX = 0, tY = 0;
            window.addEventListener('mousemove', (e) => {
                mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
                mouseY = -(e.clientY / window.innerHeight - 0.5) * 2;
            });

            // Loop 60 FPS
            function animate() {
                requestAnimationFrame(animate);
                const pos = particles.geometry.attributes.position.array;
                for (let i = 0; i < pCount * 3; i += 3) {
                    pos[i + 2] += pSpeeds[i / 3];
                    if (pos[i + 2] > 7.5) pos[i + 2] = -35;
                }
                particles.geometry.attributes.position.needsUpdate = true;
                particles.rotation.z += 0.001;

                ringsGroup.children.forEach((r, idx) => {
                    r.rotation.z += 0.003 * (idx % 2 === 0 ? 1 : -1);
                });

                tX += (mouseX * 0.5 - tX) * 0.05;
                tY += (mouseY * 0.35 - tY) * 0.05;

                const base = scenes[activeScene].cam;
                camera.position.x = base.x + tX;
                camera.position.y = base.y + tY;

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
    components.html(landing_3d_html, height=605)

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
    st.markdown("Preços transparentes para empresas individuais e gabinetes de contabilidade:")
    
    col_p1, col_p2, col_p3 = st.columns(3)

    with col_p1:
        st.markdown("""
        <div class="pricing-card">
            <div>
                <span class="badge-pill badge-turquoise">Diagnóstico</span>
                <h3 style="margin: 0; color: #ffffff;">Acesso Gratuito</h3>
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
                <span class="badge-pill badge-turquoise">Empresas</span>
                <h3 style="margin: 0; color: #ffffff;">PME Gestão</h3>
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

# ---------------- CABEÇALHO SUPERIOR DA APLICAÇÃO ----------------
st.markdown("""
<div class="main-header">
    <span class="badge-pill badge-turquoise">SAF-T Intelligence 3D • Aveiro, PT</span>
    <h1 style="margin: 0; font-size: 28px; color: #ffffff;">⚡ Analisador SAF-T | Diagnóstico Executivo</h1>
    <p style="margin: 6px 0 0 0; color: #94a3b8; font-size: 14px;">
        Importa, processa e analisa dados SAF-T com precisão | Por Igor - Junior Data Analyst
    </p>
</div>
""", unsafe_allow_html=True)

ficheiro_saft = st.file_uploader("📂 Arraste ou selecione o ficheiro SAF-T (.xml) da empresa", type=["xml"])

# ---------------- CASO 1: PÁGINA INICIAL COM O MOTOR 3D THE STATE OF THE GALLERY ----------------
if ficheiro_saft is None:
    # AWWWARDS 3D SCENE TRANSITION TURQUOISE ENGINE
    render_3d_hero_section()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Pilares de Auditoria e Inteligência:")
    col_h1, col_h2, col_h3 = st.columns(3)

    with col_h1:
        st.markdown("""
        <div class="hero-card">
            <span class="badge-pill badge-turquoise">Segurança Máxima</span>
            <h3 style="margin-top: 8px; color: #ffffff;">🔒 100% In-Memory (RGPD)</h3>
            <p style="color: #94a3b8; font-size: 14px; margin-top: 6px;">
                Os dados fiscais e listas de faturas são processados exclusivamente na memória volátil da sessão. Nenhum valor de faturação é gravado em bases de dados externas.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_h2:
        st.markdown("""
        <div class="hero-card">
            <span class="badge-pill badge-turquoise">Gestão Estratégica</span>
            <h3 style="margin-top: 8px; color: #ffffff;">📊 Curva ABC & Risco 80/20</h3>
            <p style="color: #94a3b8; font-size: 14px; margin-top: 6px;">
                Descobre instantaneamente os clientes Classe A que garantem 80% do fluxo de caixa e obtém alertas preventivos de risco de tesouraria.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_h3:
        st.markdown("""
        <div class="hero-card">
            <span class="badge-pill badge-amber">Conferência Fiscal</span>
            <h3 style="margin-top: 8px; color: #ffffff;">⚖️ Auditoria de IVA</h3>
            <p style="color: #94a3b8; font-size: 14px; margin-top: 6px;">
                Resumo instantâneo de faturas emitidas vs. notas de crédito, com conferência por taxas normal (23%), intermédia, reduzida e isenções.
            </p>
        </div>
        """, unsafe_allow_html=True)

# ---------------- CASO 2: PROCESSAMENTO E PAINEL EXECUTIVO ----------------
else:
    try:
        bytes_data = ficheiro_saft.read()
        df, df_tax = processar_saft_completo(bytes_data)

        # Métricas Globais
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
            st.line_chart(df_diario.set_index('Data'), color="#00D9D9")

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
                    <p style="color: #64748b; font-size: 13px;">Auditoria Automatizada via SAF-T | Analisador SAF-T</p>
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
                msg_whats_geral = "Olá! Estive a testar a plataforma Analisador SAF-T e gostaria de tirar algumas dúvidas sobre os planos."
                url_whatsapp = f"https://wa.me/{numero_whatsapp}?text={urllib.parse.quote(msg_whats_geral)}"
                
                st.link_button("💬 Abrir Conversa no WhatsApp", url_whatsapp, type="primary", use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao processar ficheiro SAF-T: {e}")
