"""
Three.js and WebGL Renderer Utility
Generates responsive 3D visualization components embedded via st.components.v1.html.
"""

import json
import streamlit as st
import streamlit.components.v1 as components

def get_theme_colors(theme: str):
    """Return color hexes matching the theme for WebGL styling"""
    if theme == "dark":
        return {
            "bg": "#0b0f19",
            "text": "#f8fafc",
            "text_variant": "#94a3b8",
            "border": "#334155",
            "card_bg": "rgba(30, 41, 59, 0.85)",
            "primary": "#3B82F6",
            "secondary": "#A855F7",
            "accent": "#00687a",
            "success": "#2ca02c"
        }
    else:
        return {
            "bg": "#f8fafc",
            "text": "#0b1c30",
            "text_variant": "#475569",
            "border": "#e2e8f0",
            "card_bg": "rgba(255, 255, 255, 0.9)",
            "primary": "#1E40AF",
            "secondary": "#7E22CE",
            "accent": "#00687a",
            "success": "#16A34A"
        }

def render_3d_kpis(kpi_data: list, theme: str):
    """
    Renders 8 KPI panels as floating 3D glassmorphic cards.
    kpi_data: list of dicts with keys: title, value, icon, color
    """
    colors = get_theme_colors(theme)
    data_json = json.dumps(kpi_data)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                margin: 0;
                overflow: hidden;
                background-color: {colors["bg"]};
                font-family: 'Inter', sans-serif;
            }}
            #canvas-container {{
                width: 100vw;
                height: 380px;
                position: relative;
            }}
            #tooltip-overlay {{
                position: absolute;
                bottom: 15px;
                left: 50%;
                transform: translateX(-50%);
                background: {colors["card_bg"]};
                border: 1px solid {colors["border"]};
                backdrop-filter: blur(10px);
                color: {colors["text"]};
                padding: 12px 24px;
                border-radius: 8px;
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.3s ease;
                text-align: center;
                box-shadow: 0 4px 20px rgba(0,0,0,0.25);
                font-size: 14px;
                z-index: 10;
            }}
            #instructions {{
                position: absolute;
                top: 10px;
                right: 15px;
                color: {colors["text_variant"]};
                font-size: 10px;
                text-transform: uppercase;
                letter-spacing: 1px;
                pointer-events: none;
                z-index: 10;
            }}
        </style>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Hanken+Grotesk:wght@700;800&display=swap" rel="stylesheet">
        <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    </head>
    <body>
        <div id="canvas-container">
            <div id="instructions">DRAG TO ORBIT | HOVER CARDS</div>
            <div id="tooltip-overlay"></div>
        </div>
        
        <script>
            const kpiData = {data_json};
            const theme = "{theme}";
            const colors = {json.dumps(colors)};
            
            const container = document.getElementById('canvas-container');
            const tooltip = document.getElementById('tooltip-overlay');
            
            let scene, camera, renderer, controls, clock, raycaster;
            const mouse = new THREE.Vector2();
            let hoveredCard = null;
            const cards = [];
            let particleSystem;
            
            // Setup responsive camera spacing & geometry
            const columns = 4;
            const rows = 2;
            const spacingX = 3.9;
            const spacingY = 2.1;
            const cardGeometry = new THREE.PlaneGeometry(3.0, 1.5);
            
            function createCardTexture(data) {{
                const canvas = document.createElement('canvas');
                canvas.width = 512;
                canvas.height = 256;
                const ctx = canvas.getContext('2d');
                
                // Card Background
                ctx.fillStyle = theme === 'dark' ? 'rgba(15, 23, 42, 0.95)' : 'rgba(255, 255, 255, 0.95)';
                ctx.beginPath();
                ctx.roundRect(0, 0, 512, 256, 24);
                ctx.fill();
                
                // Top Color Bar
                ctx.fillStyle = data.color;
                ctx.beginPath();
                ctx.roundRect(0, 0, 512, 16, [24, 24, 0, 0]);
                ctx.fill();
                
                // Border Stroke
                ctx.strokeStyle = theme === 'dark' ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)';
                ctx.lineWidth = 4;
                ctx.stroke();
                
                // Text - Title
                ctx.fillStyle = theme === 'dark' ? '#94a3b8' : '#475569';
                ctx.font = 'bold 20px Inter, sans-serif';
                ctx.fillText(data.title.toUpperCase(), 36, 60);
                
                // Text - Value
                ctx.fillStyle = theme === 'dark' ? '#f8fafc' : '#0b1c30';
                ctx.font = '800 64px Hanken Grotesk, sans-serif';
                ctx.fillText(data.value, 36, 160);
                
                // Icon (Text representation for safety, fallback to emojis if web font fails)
                const isFontLoaded = document.fonts.check('24px "Material Icons"');
                if (isFontLoaded) {{
                    ctx.fillStyle = data.color;
                    ctx.font = '48px "Material Icons"';
                    ctx.fillText(data.icon, 410, 90);
                }} else {{
                    const emojiMap = {{
                        'group': '👥',
                        'bolt': '⚡',
                        'track_changes': '🎯',
                        'science': '🧪',
                        'biotech': '🔬',
                        'settings': '⚙️',
                        'bubble_chart': '📊',
                        'description': '📄'
                    }};
                    ctx.font = '44px sans-serif';
                    ctx.fillText(emojiMap[data.icon] || '📊', 410, 90);
                }}
                
                // Description/Conf
                ctx.fillStyle = theme === 'dark' ? 'rgba(148,163,184,0.6)' : 'rgba(71,85,105,0.6)';
                ctx.font = '14px Inter, sans-serif';
                ctx.fillText('ACTIVE METRIC', 36, 215);
                
                const texture = new THREE.CanvasTexture(canvas);
                texture.minFilter = THREE.LinearFilter;
                return texture;
            }}
            
            function updateCamera() {{
                const aspect = container.clientWidth / container.clientHeight;
                camera.aspect = aspect;
                
                // Dynamically scale camera Z distance to fit 4-column cards cleanly on narrow viewports
                if (aspect < 1.7) {{
                    camera.position.z = 11.5 * (1.7 / aspect);
                }} else {{
                    camera.position.z = 11.5;
                }}
                camera.updateProjectionMatrix();
            }}
            
            function init() {{
                // Setup scene
                scene = new THREE.Scene();
                scene.fog = new THREE.FogExp2(colors.bg, 0.015);
                
                // Camera
                camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
                
                // Renderer
                renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
                renderer.setSize(container.clientWidth, container.clientHeight);
                renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
                container.appendChild(renderer.domElement);
                
                // Adjust camera initially
                updateCamera();
                
                // Controls
                controls = new THREE.OrbitControls(camera, renderer.domElement);
                controls.enableDamping = true;
                controls.dampingFactor = 0.05;
                controls.maxPolarAngle = Math.PI / 2 + 0.1;
                controls.minPolarAngle = Math.PI / 4;
                controls.enableZoom = true;
                controls.maxDistance = 25;
                controls.minDistance = 6;
                
                // Lights
                const ambientLight = new THREE.AmbientLight(theme === 'dark' ? 0x222222 : 0x888888);
                scene.add(ambientLight);
                
                const dirLight1 = new THREE.DirectionalLight(0xffffff, 0.8);
                dirLight1.position.set(5, 10, 7);
                scene.add(dirLight1);
                
                const pointLight = new THREE.PointLight(colors.primary, 1.5, 30);
                pointLight.position.set(0, 0, 0);
                scene.add(pointLight);
                
                // Create card meshes
                kpiData.forEach((data, index) => {{
                    const col = index % columns;
                    const row = Math.floor(index / columns);
                    
                    const texture = createCardTexture(data);
                    const material = new THREE.MeshBasicMaterial({{
                        map: texture,
                        transparent: true,
                        opacity: 0.9,
                        side: THREE.DoubleSide
                    }});
                    
                    const mesh = new THREE.Mesh(cardGeometry, material);
                    
                    // Position in grid
                    const x = (col - (columns - 1) / 2) * spacingX;
                    const y = ((rows - 1) / 2 - row) * spacingY;
                    const z = -Math.pow(Math.abs(x), 2) * 0.04; // Very subtle curved arc to prevent clipping
                    
                    mesh.position.set(x, y, z);
                    mesh.userData = {{
                        originalPos: new THREE.Vector3(x, y, z),
                        data: data,
                        index: index,
                        floatOffset: Math.random() * Math.PI * 2
                    }};
                    
                    scene.add(mesh);
                    cards.push(mesh);
                }});
                
                // Dust Particles Background
                const particleCount = 180;
                const particlesGeom = new THREE.BufferGeometry();
                const positions = [];
                
                for (let i = 0; i < particleCount; i++) {{
                    positions.push((Math.random() - 0.5) * 25);
                    positions.push((Math.random() - 0.5) * 15);
                    positions.push((Math.random() - 0.5) * 15);
                }}
                
                particlesGeom.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
                
                const particlesMaterial = new THREE.PointsMaterial({{
                    color: colors.primary,
                    size: 0.06,
                    transparent: true,
                    opacity: 0.4
                }});
                
                particleSystem = new THREE.Points(particlesGeom, particlesMaterial);
                scene.add(particleSystem);
                
                // Raycaster
                raycaster = new THREE.Raycaster();
                clock = new THREE.Clock();
                
                window.addEventListener('mousemove', (e) => {{
                    const rect = renderer.domElement.getBoundingClientRect();
                    mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
                    mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
                }});
                
                // Resize handler
                window.addEventListener('resize', () => {{
                    updateCamera();
                    renderer.setSize(container.clientWidth, container.clientHeight);
                }});
                
                animate();
            }}
            
            function animate() {{
                requestAnimationFrame(animate);
                
                const time = clock.getElapsedTime();
                
                // Extremely subtle breathing/floating animation to keep cards clean and readable
                cards.forEach(card => {{
                    card.position.y = card.userData.originalPos.y + Math.sin(time + card.userData.floatOffset) * 0.03;
                    card.rotation.y = Math.sin(time + card.userData.floatOffset) * 0.01;
                }});
                
                // Rotate dust
                if (particleSystem) {{
                    particleSystem.rotation.y = time * 0.003;
                }}
                
                // Interaction Raycast
                raycaster.setFromCamera(mouse, camera);
                const intersects = raycaster.intersectObjects(cards);
                
                if (intersects.length > 0) {{
                    const hitCard = intersects[0].object;
                    if (hoveredCard !== hitCard) {{
                        if (hoveredCard) {{
                            hoveredCard.scale.set(1, 1, 1);
                            hoveredCard.material.opacity = 0.9;
                        }}
                        hoveredCard = hitCard;
                        hoveredCard.scale.set(1.05, 1.05, 1.05);
                        hoveredCard.material.opacity = 1.0;
                        
                        tooltip.style.opacity = 1;
                        tooltip.innerHTML = `<strong>${{hoveredCard.userData.data.title}}</strong>: <span style="color:${{hoveredCard.userData.data.color}}">${{hoveredCard.userData.data.value}}</span>`;
                    }}
                }} else {{
                    if (hoveredCard) {{
                        hoveredCard.scale.set(1, 1, 1);
                        hoveredCard.material.opacity = 0.9;
                        hoveredCard = null;
                        tooltip.style.opacity = 0;
                    }}
                }}
                
                controls.update();
                renderer.render(scene, camera);
            }}
            
            // Wait for Google Fonts & Material Icons to be ready before drawing
            document.fonts.ready.then(() => {{
                // Extra short timeout to ensure the fonts are bound to document context
                setTimeout(init, 50);
            }}).catch(err => {{
                console.warn("Font loader failed, initializing immediately:", err);
                init();
            }});
        </script>
    </body>
    </html>
    """
    components.html(html, height=380)

def render_3d_funnel(funnel_data: list, theme: str):
    """
    Renders the 9 pipeline stages as a 3D rotatable glowing stack of circular segments.
    """
    colors = get_theme_colors(theme)
    data_json = json.dumps(funnel_data)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                margin: 0;
                overflow: hidden;
                background-color: {colors["bg"]};
                font-family: 'Inter', sans-serif;
            }}
            #container {{
                display: flex;
                width: 100vw;
                height: 480px;
                position: relative;
            }}
            #canvas {{
                flex: 1.5;
                height: 100%;
            }}
            #info-pane {{
                flex: 1;
                background: {colors["card_bg"]};
                border-left: 1px solid {colors["border"]};
                backdrop-filter: blur(12px);
                color: {colors["text"]};
                padding: 24px;
                box-sizing: border-box;
                display: flex;
                flex-direction: column;
                justify-content: center;
                overflow-y: auto;
            }}
            .metric-val {{
                font-family: 'Hanken Grotesk', sans-serif;
                font-size: 38px;
                font-weight: 800;
                margin-top: 5px;
                margin-bottom: 5px;
            }}
            .badge {{
                display: inline-block;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 10px;
                font-weight: bold;
                text-transform: uppercase;
                margin-bottom: 12px;
            }}
            #controls-hint {{
                position: absolute;
                bottom: 15px;
                left: 15px;
                color: {colors["text_variant"]};
                font-size: 10px;
                text-transform: uppercase;
                letter-spacing: 1px;
                pointer-events: none;
            }}
        </style>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Hanken+Grotesk:wght@800&display=swap" rel="stylesheet">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    </head>
    <body>
        <div id="container">
            <div id="canvas"></div>
            <div id="info-pane">
                <span class="badge" id="info-badge" style="background: rgba(59, 130, 246, 0.15); color: #3b82f6;">Pipeline Stage</span>
                <h2 style="margin: 0; font-weight: 700; font-size: 20px;" id="info-title">Hover a stage</h2>
                <div class="metric-val" id="info-count">-</div>
                <div style="font-size: 13px; color: {colors["text_variant"]}; margin-bottom: 20px;" id="info-desc">
                    Hover or click the 3D pipeline stages to see throughput counts, conversion rates, and insights.
                </div>
                <div id="info-conversion" style="font-size: 12px; border-top: 1px dashed {colors["border"]}; padding-top: 15px;">
                    <strong>Conversion Efficiency:</strong> <span id="info-conv-val">-</span>
                </div>
            </div>
            <div id="controls-hint">ROTATE: DRAG | ZOOM: SCROLL</div>
        </div>
        
        <script>
            const funnelData = {data_json};
            const theme = "{theme}";
            const colors = {json.dumps(colors)};
            
            const canvasContainer = document.getElementById('canvas');
            const infoTitle = document.getElementById('info-title');
            const infoCount = document.getElementById('info-count');
            const infoDesc = document.getElementById('info-desc');
            const infoBadge = document.getElementById('info-badge');
            const infoConvVal = document.getElementById('info-conv-val');
            
            // Three.js Setup
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(40, canvasContainer.clientWidth / canvasContainer.clientHeight, 0.1, 1000);
            camera.position.set(0, 3, 10);
            
            const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
            renderer.setSize(canvasContainer.clientWidth, canvasContainer.clientHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            canvasContainer.appendChild(renderer.domElement);
            
            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            controls.maxPolarAngle = Math.PI / 2 + 0.3;
            controls.minPolarAngle = 0.2;
            controls.enableZoom = true;
            
            // Lighting
            scene.add(new THREE.AmbientLight(0xffffff, theme === 'dark' ? 0.3 : 0.7));
            const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
            dirLight.position.set(5, 15, 5);
            scene.add(dirLight);
            
            // Build the 3D funnel stack
            const rings = [];
            const ringCount = funnelData.length;
            const startRadius = 3.2;
            const endRadius = 0.8;
            const totalHeight = 5.0;
            const heightStep = totalHeight / (ringCount - 1);
            
            // Color map helper
            const ringColors = [
                '#3B82F6', '#06B6D4', '#00687a', '#A855F7', '#D946EF',
                '#EC4899', '#F43F5E', '#10B981', '#2ca02c'
            ];
            
            funnelData.forEach((stage, idx) => {{
                // Interpolate radius from top to bottom
                const factor = idx / (ringCount - 1);
                const radius = startRadius - factor * (startRadius - endRadius);
                const yPos = totalHeight / 2 - idx * heightStep;
                
                // Geometry - Torus/Tubes
                const ringGeom = new THREE.TorusGeometry(radius, 0.12, 16, 100);
                const color = ringColors[idx % ringColors.length];
                const ringMat = new THREE.MeshStandardMaterial({{
                    color: color,
                    roughness: 0.1,
                    metalness: 0.8,
                    emissive: color,
                    emissiveIntensity: 0.15
                }});
                
                const mesh = new THREE.Mesh(ringGeom, ringMat);
                mesh.rotation.x = Math.PI / 2;
                mesh.position.set(0, yPos, 0);
                
                // Add transparent funnel connector cone
                if (idx < ringCount - 1) {{
                    const nextRadius = startRadius - ((idx + 1) / (ringCount - 1)) * (startRadius - endRadius);
                    const coneGeom = new THREE.CylinderGeometry(radius, nextRadius, heightStep, 32, 1, true);
                    const coneMat = new THREE.MeshBasicMaterial({{
                        color: color,
                        transparent: true,
                        opacity: 0.08,
                        side: THREE.DoubleSide,
                        wireframe: true
                    }});
                    const coneMesh = new THREE.Mesh(coneGeom, coneMat);
                    coneMesh.position.set(0, yPos - heightStep / 2, 0);
                    scene.add(coneMesh);
                }}
                
                mesh.userData = {{
                    data: stage,
                    color: color,
                    originalScale: new THREE.Vector3(1, 1, 1),
                    idx: idx
                }};
                
                scene.add(mesh);
                rings.push(mesh);
            }});
            
            // Falling molecules simulation
            const particleCount = 60;
            const particleGeom = new THREE.SphereGeometry(0.04, 8, 8);
            const particleMat = new THREE.MeshBasicMaterial({{ color: '#ffffff', transparent: true, opacity: 0.8 }});
            const particles = [];
            
            for (let i = 0; i < particleCount; i++) {{
                const mesh = new THREE.Mesh(particleGeom, particleMat);
                resetParticle(mesh);
                scene.add(mesh);
                particles.push(mesh);
            }}
            
            function resetParticle(mesh) {{
                const startIdx = Math.floor(Math.random() * (ringCount - 1));
                const endIdx = startIdx + 1;
                
                const factorStart = startIdx / (ringCount - 1);
                const factorEnd = endIdx / (ringCount - 1);
                
                const radStart = startRadius - factorStart * (startRadius - endRadius);
                const radEnd = startRadius - factorEnd * (startRadius - endRadius);
                
                const yStart = totalHeight / 2 - startIdx * heightStep;
                const yEnd = totalHeight / 2 - endIdx * heightStep;
                
                // Random angle on ring
                const angle = Math.random() * Math.PI * 2;
                
                mesh.position.set(Math.cos(angle) * radStart, yStart, Math.sin(angle) * radStart);
                
                mesh.userData = {{
                    angle: angle,
                    speed: 0.015 + Math.random() * 0.02,
                    startIdx: startIdx,
                    endIdx: endIdx,
                    radStart: radStart,
                    radEnd: radEnd,
                    yStart: yStart,
                    yEnd: yEnd,
                    t: 0
                }};
            }}
            
            // Raycasting
            const raycaster = new THREE.Raycaster();
            const mouse = new THREE.Vector2();
            let hoveredRing = null;
            
            window.addEventListener('mousemove', (e) => {{
                const rect = renderer.domElement.getBoundingClientRect();
                mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
                mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
            }});
            
            window.addEventListener('click', () => {{
                if (hoveredRing) {{
                    updateSidebar(hoveredRing.userData.data, hoveredRing.userData.color);
                }}
            }});
            
            function updateSidebar(data, color) {{
                infoBadge.style.background = color + "22";
                infoBadge.style.color = color;
                infoTitle.innerText = data.stage;
                infoCount.innerText = Number(data.count).toLocaleString();
                infoCount.style.color = color;
                infoDesc.innerText = data.description || `Pipeline analytics details for Stage ${{data.stage}}. Tracked molecules: ${{data.count}}.`;
                infoConvVal.innerText = data.conversion_rate !== undefined ? `${{data.conversion_rate}}%` : '100% (Baseline)';
            }}
            
            // Set initial sidebar details
            if (funnelData.length > 0) {{
                updateSidebar(funnelData[0], ringColors[0]);
            }}
            
            // Animation Loop
            function animate() {{
                requestAnimationFrame(animate);
                
                // Spin rings
                rings.forEach((ring, idx) => {{
                    ring.rotation.z += 0.003 * (idx % 2 === 0 ? 1 : -1);
                }});
                
                // Particles flow
                particles.forEach(p => {{
                    p.userData.t += p.userData.speed;
                    if (p.userData.t >= 1) {{
                        resetParticle(p);
                    }} else {{
                        const t = p.userData.t;
                        const rad = p.userData.radStart * (1 - t) + p.userData.radEnd * t;
                        const y = p.userData.yStart * (1 - t) + p.userData.yEnd * t;
                        const angle = p.userData.angle + t * 0.5; // Slight twist
                        
                        p.position.set(Math.cos(angle) * rad, y, Math.sin(angle) * rad);
                    }}
                }});
                
                // Raycasting check
                raycaster.setFromCamera(mouse, camera);
                const intersects = raycaster.intersectObjects(rings);
                
                if (intersects.length > 0) {{
                    const hit = intersects[0].object;
                    if (hoveredRing !== hit) {{
                        if (hoveredRing) {{
                            hoveredRing.material.emissiveIntensity = 0.15;
                        }}
                        hoveredRing = hit;
                        hoveredRing.material.emissiveIntensity = 0.7;
                        updateSidebar(hoveredRing.userData.data, hoveredRing.userData.color);
                    }}
                }} else {{
                    if (hoveredRing) {{
                        hoveredRing.material.emissiveIntensity = 0.15;
                        hoveredRing = null;
                    }}
                }}
                
                controls.update();
                renderer.render(scene, camera);
            }}
            
            animate();
            
            window.addEventListener('resize', () => {{
                camera.aspect = canvasContainer.clientWidth / canvasContainer.clientHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(canvasContainer.clientWidth, canvasContainer.clientHeight);
            }});
        </script>
    </body>
    </html>
    """
    components.html(html, height=480)

def render_3d_user_clustering(users_list: list, theme: str):
    """
    Renders user nodes in 3D force clustering grouped by department.
    """
    colors = get_theme_colors(theme)
    data_json = json.dumps(users_list)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                margin: 0;
                overflow: hidden;
                background-color: {colors["bg"]};
                font-family: 'Inter', sans-serif;
            }}
            #container {{
                width: 100vw;
                height: 480px;
                position: relative;
            }}
            #tooltip {{
                position: absolute;
                top: 15px;
                left: 15px;
                background: {colors["card_bg"]};
                border: 1px solid {colors["border"]};
                padding: 16px;
                border-radius: 8px;
                color: {colors["text"]};
                font-size: 13px;
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.3s ease;
                min-width: 200px;
                box-shadow: 0 4px 25px rgba(0,0,0,0.3);
            }}
            #legend {{
                position: absolute;
                bottom: 15px;
                right: 15px;
                background: {colors["card_bg"]};
                border: 1px solid {colors["border"]};
                padding: 10px;
                border-radius: 6px;
                color: {colors["text"]};
                font-size: 10px;
                display: flex;
                flex-direction: column;
                gap: 4px;
            }}
            .legend-item {{
                display: flex;
                align-items: center;
                gap: 6px;
            }}
            .dot {{
                width: 8px;
                height: 8px;
                border-radius: 50%;
            }}
        </style>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    </head>
    <body>
        <div id="container">
            <div id="tooltip">Hover a node</div>
            <div id="legend"></div>
        </div>
        
        <script>
            const users = {data_json};
            const theme = "{theme}";
            const colors = {json.dumps(colors)};
            
            const container = document.getElementById('container');
            const tooltip = document.getElementById('tooltip');
            const legend = document.getElementById('legend');
            
            // Scene Setup
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
            camera.position.set(0, 0, 12);
            
            const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
            renderer.setSize(container.clientWidth, container.clientHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            container.appendChild(renderer.domElement);
            
            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            
            scene.add(new THREE.AmbientLight(0xffffff, theme === 'dark' ? 0.4 : 0.8));
            const pLight = new THREE.PointLight(0xffffff, 1.2, 50);
            pLight.position.set(5, 5, 5);
            scene.add(pLight);
            
            // Setup department colors
            const depts = [...new Set(users.map(u => u.department || 'General'))];
            const deptColors = {{}};
            const colorPalette = ['#3B82F6', '#A855F7', '#10B981', '#06B6D4', '#EC4899', '#F59E0B'];
            
            depts.forEach((d, idx) => {{
                deptColors[d] = colorPalette[idx % colorPalette.length];
                
                // Add to legend
                const item = document.createElement('div');
                item.className = 'legend-item';
                item.innerHTML = `<span class="dot" style="background:${{deptColors[d]}}"></span><span>${{d}}</span>`;
                legend.appendChild(item);
            }});
            
            // Build Nodes
            const nodes = [];
            const nodeGeom = new THREE.SphereGeometry(0.2, 32, 32);
            
            // Target cluster centers
            const clusterCenters = {{}};
            depts.forEach((d, idx) => {{
                const angle = (idx / depts.length) * Math.PI * 2;
                clusterCenters[d] = new THREE.Vector3(Math.cos(angle) * 3, Math.sin(angle) * 3, 0);
            }});
            
            users.forEach((user, idx) => {{
                const dept = user.department || 'General';
                const color = deptColors[dept];
                const mat = new THREE.MeshStandardMaterial({{
                    color: color,
                    roughness: 0.2,
                    metalness: 0.5,
                    emissive: color,
                    emissiveIntensity: 0.1
                }});
                
                const mesh = new THREE.Mesh(nodeGeom, mat);
                
                // Position randomly around department center
                const center = clusterCenters[dept];
                const offset = new THREE.Vector3(
                    (Math.random() - 0.5) * 1.5,
                    (Math.random() - 0.5) * 1.5,
                    (Math.random() - 0.5) * 1.5
                );
                mesh.position.copy(center).add(offset);
                
                mesh.userData = {{
                    user: user,
                    color: color,
                    velocity: new THREE.Vector3()
                }};
                
                scene.add(mesh);
                nodes.push(mesh);
            }});
            
            // Lines connecting nodes in the same department
            const lineMat = new THREE.LineBasicMaterial({{
                color: theme === 'dark' ? 0x334155 : 0xcbd5e1,
                transparent: true,
                opacity: 0.15
            }});
            
            const linePositions = [];
            for (let i = 0; i < nodes.length; i++) {{
                for (let j = i + 1; j < nodes.length; j++) {{
                    if (nodes[i].userData.user.department === nodes[j].userData.user.department) {{
                        linePositions.push(nodes[i].position);
                        linePositions.push(nodes[j].position);
                    }}
                }}
            }}
            
            const lineGeom = new THREE.BufferGeometry().setFromPoints(linePositions);
            const connections = new THREE.LineSegments(lineGeom, lineMat);
            scene.add(connections);
            
            // Physics forces (Force-directed layout step)
            function updatePhysics() {{
                const kCluster = 0.05; // Cluster pull force
                const kRepel = 0.03;   // Repulsion between nodes
                const kCenter = 0.01;  // Pull to grid origin
                
                // 1. Repel from each other
                for (let i = 0; i < nodes.length; i++) {{
                    for (let j = i + 1; j < nodes.length; j++) {{
                        const dir = new THREE.Vector3().subVectors(nodes[i].position, nodes[j].position);
                        const dist = dir.length();
                        if (dist < 2.0 && dist > 0.01) {{
                            dir.normalize().multiplyScalar(kRepel / dist);
                            nodes[i].userData.velocity.add(dir);
                            nodes[j].userData.velocity.sub(dir);
                        }}
                    }}
                    
                    // 2. Pull toward cluster center
                    const dept = nodes[i].userData.user.department || 'General';
                    const center = clusterCenters[dept];
                    const dirToCenter = new THREE.Vector3().subVectors(center, nodes[i].position);
                    dirToCenter.multiplyScalar(kCluster);
                    nodes[i].userData.velocity.add(dirToCenter);
                    
                    // 3. Central gravity
                    const dirToOrigin = new THREE.Vector3().copy(nodes[i].position).multiplyScalar(-kCenter);
                    nodes[i].userData.velocity.add(dirToOrigin);
                }}
                
                // Update position
                nodes.forEach(n => {{
                    n.position.add(n.userData.velocity);
                    n.userData.velocity.multiplyScalar(0.85); // Damping
                }});
                
                // Rebuild connecting lines
                const linePts = [];
                for (let i = 0; i < nodes.length; i++) {{
                    for (let j = i + 1; j < nodes.length; j++) {{
                        if (nodes[i].userData.user.department === nodes[j].userData.user.department) {{
                            linePts.push(nodes[i].position);
                            linePts.push(nodes[j].position);
                        }}
                    }}
                }}
                connections.geometry.setFromPoints(linePts);
            }}
            
            // Interaction
            const raycaster = new THREE.Raycaster();
            const mouse = new THREE.Vector2();
            let hoveredNode = null;
            
            window.addEventListener('mousemove', (e) => {{
                const rect = renderer.domElement.getBoundingClientRect();
                mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
                mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
            }});
            
            function animate() {{
                requestAnimationFrame(animate);
                
                updatePhysics();
                
                // Raycasting
                raycaster.setFromCamera(mouse, camera);
                const intersects = raycaster.intersectObjects(nodes);
                
                if (intersects.length > 0) {{
                    const hit = intersects[0].object;
                    if (hoveredNode !== hit) {{
                        if (hoveredNode) {{
                            hoveredNode.scale.set(1, 1, 1);
                            hoveredNode.material.emissiveIntensity = 0.1;
                        }}
                        hoveredNode = hit;
                        hoveredNode.scale.set(1.5, 1.5, 1.5);
                        hoveredNode.material.emissiveIntensity = 0.5;
                        
                        const u = hoveredNode.userData.user;
                        tooltip.style.opacity = 1;
                        tooltip.innerHTML = `
                            <strong style="color:${{hoveredNode.userData.color}}">${{u.email || u.user_id}}</strong><br>
                            Department: ${{u.department || 'N/A'}}<br>
                            Role: ${{u.role || 'Scientist'}}<br>
                            Activity count: ${{u.activity_count || u.views || 0}}
                        `;
                    }}
                }} else {{
                    if (hoveredNode) {{
                        hoveredNode.scale.set(1, 1, 1);
                        hoveredNode.material.emissiveIntensity = 0.1;
                        hoveredNode = null;
                        tooltip.style.opacity = 0;
                    }}
                }}
                
                controls.update();
                renderer.render(scene, camera);
            }}
            
            animate();
            
            window.addEventListener('resize', () => {{
                camera.aspect = container.clientWidth / container.clientHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(container.clientWidth, container.clientHeight);
            }});
        </script>
    </body>
    </html>
    """
    components.html(html, height=480)

def render_3d_molecule_viewer(energy: float, theme: str):
    """
    Procedural 3D Molecular Viewer inside a glowing binding pocket.
    """
    colors = get_theme_colors(theme)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                margin: 0;
                overflow: hidden;
                background-color: #0b0f19;
                font-family: 'Inter', sans-serif;
            }}
            #container {{
                width: 100vw;
                height: 360px;
                position: relative;
            }}
            #info {{
                position: absolute;
                bottom: 12px;
                left: 12px;
                background: rgba(15, 23, 42, 0.85);
                border: 1px solid rgba(255, 255, 255, 0.1);
                color: #f8fafc;
                font-size: 11px;
                padding: 6px 12px;
                border-radius: 4px;
            }}
        </style>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    </head>
    <body>
        <div id="container">
            <div id="info">BINDING AFFINITY: <strong style="color:#A855F7;">{energy} kcal/mol</strong></div>
        </div>
        
        <script>
            const energy = {energy};
            const theme = "{theme}";
            const container = document.getElementById('container');
            
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(40, container.clientWidth / container.clientHeight, 0.1, 1000);
            camera.position.set(0, 0, 7);
            
            const renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(container.clientWidth, container.clientHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            container.appendChild(renderer.domElement);
            
            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            
            // Lights
            scene.add(new THREE.AmbientLight(0x444444));
            const dLight = new THREE.DirectionalLight(0xffffff, 1.0);
            dLight.position.set(5, 5, 5);
            scene.add(dLight);
            
            // Create Mock Binding Pocket Ribbon (Procedural Double Helix)
            const helixGroup = new THREE.Group();
            const tubeGeom = new THREE.CylinderGeometry(0.06, 0.06, 8, 16);
            const tubeMat = new THREE.MeshStandardMaterial({{ color: '#334155', roughness: 0.4 }});
            
            const helixCount = 2;
            const pointsCount = 60;
            const radius = 1.6;
            
            for (let h = 0; h < helixCount; h++) {{
                const pts = [];
                for (let i = 0; i < pointsCount; i++) {{
                    const t = i / pointsCount;
                    const angle = t * Math.PI * 6 + (h * Math.PI);
                    const y = (t - 0.5) * 4.5;
                    pts.push(new THREE.Vector3(Math.cos(angle) * radius, y, Math.sin(angle) * radius));
                }}
                
                const curve = new THREE.CatmullRomCurve3(pts);
                const geom = new THREE.TubeGeometry(curve, 64, 0.08, 8, false);
                const mat = new THREE.MeshStandardMaterial({{
                    color: h === 0 ? '#00687a' : '#3B82F6',
                    roughness: 0.1,
                    metalness: 0.7
                }});
                helixGroup.add(new THREE.Mesh(geom, mat));
            }}
            scene.add(helixGroup);
            
            // Ligand Ball-and-Stick Model
            const ligandGroup = new THREE.Group();
            const atomColors = ['#ef4444', '#10b981', '#3b82f6', '#f59e0b', '#ec4899'];
            const atomCount = 14;
            const atoms = [];
            
            // Generate atom points
            for (let i = 0; i < atomCount; i++) {{
                const theta = Math.random() * Math.PI * 2;
                const phi = Math.acos((Math.random() * 2) - 1);
                const r = Math.random() * 0.7; // Kept tight in pocket
                const pos = new THREE.Vector3(
                    Math.sin(phi) * Math.cos(theta) * r,
                    Math.sin(phi) * Math.sin(theta) * r,
                    Math.cos(phi) * r
                );
                
                const c = atomColors[i % atomColors.length];
                const sphere = new THREE.Mesh(
                    new THREE.SphereGeometry(0.12, 16, 16),
                    new THREE.MeshStandardMaterial({{ color: c, metalness: 0.5, roughness: 0.2 }})
                );
                sphere.position.copy(pos);
                ligandGroup.add(sphere);
                atoms.push(pos);
            }}
            
            // Generate stick connections (bonds)
            for (let i = 0; i < atomCount; i++) {{
                // Connect to 1 or 2 closest neighbors
                const dists = atoms.map((p, idx) => ({{ idx, d: p.distanceTo(atoms[i]) }}))
                                   .filter(x => x.idx !== i)
                                   .sort((a, b) => a.d - b.d);
                
                for (let k = 0; k < Math.min(2, dists.length); k++) {{
                    const target = atoms[dists[k].idx];
                    const direction = new THREE.Vector3().subVectors(target, atoms[i]);
                    const length = direction.length();
                    
                    const cylGeom = new THREE.CylinderGeometry(0.04, 0.04, length, 8);
                    const cylMat = new THREE.MeshStandardMaterial({{ color: '#ffffff', roughness: 0.6 }});
                    const bond = new THREE.Mesh(cylGeom, cylMat);
                    
                    // Align cylinder between the two atoms
                    bond.position.copy(atoms[i]).add(direction.clone().multiplyScalar(0.5));
                    
                    const up = new THREE.Vector3(0, 1, 0);
                    const alignAxis = direction.clone().normalize();
                    bond.quaternion.setFromUnitVectors(up, alignAxis);
                    
                    ligandGroup.add(bond);
                }}
            }}
            scene.add(ligandGroup);
            
            // Binding Affinity Energy Cloud (glowing heat zone sphere)
            const heatZoneMat = new THREE.MeshBasicMaterial({{
                color: '#A855F7',
                transparent: true,
                opacity: 0.22,
                wireframe: true
            }});
            const heatZone = new THREE.Mesh(new THREE.SphereGeometry(1.0, 32, 32), heatZoneMat);
            scene.add(heatZone);
            
            function animate() {{
                requestAnimationFrame(animate);
                
                const time = Date.now() * 0.0006;
                
                // Spin helix
                helixGroup.rotation.y = time * 0.15;
                
                // Jiggle ligand in pocket
                ligandGroup.rotation.y = time * 0.3;
                ligandGroup.rotation.x = Math.sin(time) * 0.1;
                
                // Pulse heat zone
                const scale = 1.0 + Math.sin(time * 3) * 0.08;
                heatZone.scale.set(scale, scale, scale);
                
                controls.update();
                renderer.render(scene, camera);
            }}
            
            animate();
            
            window.addEventListener('resize', () => {{
                camera.aspect = container.clientWidth / container.clientHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(container.clientWidth, container.clientHeight);
            }});
        </script>
    </body>
    </html>
    """
    components.html(html, height=360)

def render_3d_admet_cube(candidates: list, theme: str):
    """
    3D Drug Likeness scatter cube.
    """
    colors = get_theme_colors(theme)
    # Extract candidate data
    points = []
    import hashlib
    for idx, c in enumerate(candidates):
        cid = c.get('candidate_id', f'Cand-{idx}')
        score = c.get('optimization_score', 50)
        h = int(hashlib.md5(cid.encode()).hexdigest(), 16)
        
        # generate pseudo 3D scatter coordinate within standard bounds
        mw = round(300 + (score * 2.5) + (h % 100), 1)      # 300 - 650 g/mol
        logp = round(1.0 + (score / 25) - ((h >> 4) % 4), 2) # 0.0 - 5.0
        sol = round(-2.0 - (logp * 0.8) + ((h >> 8) % 3), 2)  # -6.0 - 1.0
        
        points.append({
            "id": cid,
            "mw": mw,
            "logp": logp,
            "solubility": sol,
            "score": score
        })
        
    points_json = json.dumps(points)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                margin: 0;
                overflow: hidden;
                background-color: {colors["bg"]};
                font-family: 'Inter', sans-serif;
            }}
            #container {{
                width: 100vw;
                height: 380px;
                position: relative;
            }}
            #tooltip {{
                position: absolute;
                top: 12px;
                right: 12px;
                background: {colors["card_bg"]};
                border: 1px solid {colors["border"]};
                padding: 12px;
                border-radius: 6px;
                color: {colors["text"]};
                font-size: 11px;
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.3s ease;
                min-width: 180px;
            }}
        </style>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    </head>
    <body>
        <div id="container">
            <div id="tooltip">Hover point</div>
        </div>
        
        <script>
            const data = {points_json};
            const theme = "{theme}";
            const colors = {json.dumps(colors)};
            const container = document.getElementById('container');
            const tooltip = document.getElementById('tooltip');
            
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(40, container.clientWidth / container.clientHeight, 0.1, 1000);
            camera.position.set(4, 4, 7);
            
            const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
            renderer.setSize(container.clientWidth, container.clientHeight);
            container.appendChild(renderer.domElement);
            
            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            
            scene.add(new THREE.AmbientLight(0xffffff, theme === 'dark' ? 0.3 : 0.7));
            const pLight = new THREE.PointLight(0xffffff, 1.0);
            pLight.position.set(5, 5, 5);
            scene.add(pLight);
            
            // Draw ADMET Bounding Wireframe Box
            const size = 3;
            const gridHelper = new THREE.BoxHelper(
                new THREE.Mesh(new THREE.BoxGeometry(size, size, size)),
                colors.border
            );
            scene.add(gridHelper);
            
            // Plot Candidates as Spheres inside the Box
            const pointGroup = new THREE.Group();
            const sphereGeom = new THREE.SphereGeometry(0.08, 16, 16);
            
            data.forEach(p => {{
                // Map values to [-size/2, size/2]
                const x = ((p.mw - 300) / 350 - 0.5) * size;      // MW
                const y = ((p.logp - 0) / 6 - 0.5) * size;        // LogP
                const z = ((p.solubility + 6) / 7 - 0.5) * size;  // Solubility
                
                const c = p.score > 80 ? '#10b981' : (p.score > 55 ? '#3B82F6' : '#FF4B4B');
                const mat = new THREE.MeshStandardMaterial({{
                    color: c,
                    roughness: 0.1,
                    metalness: 0.5,
                    emissive: c,
                    emissiveIntensity: 0.2
                }});
                
                const mesh = new THREE.Mesh(sphereGeom, mat);
                mesh.position.set(x, y, z);
                mesh.userData = {{ info: p, color: c }};
                pointGroup.add(mesh);
            }});
            scene.add(pointGroup);
            
            // Raycast
            const raycaster = new THREE.Raycaster();
            const mouse = new THREE.Vector2();
            let hoveredPoint = null;
            
            window.addEventListener('mousemove', (e) => {{
                const rect = renderer.domElement.getBoundingClientRect();
                mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
                mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
            }});
            
            function animate() {{
                requestAnimationFrame(animate);
                
                pointGroup.rotation.y += 0.002; // slow rot
                
                raycaster.setFromCamera(mouse, camera);
                const intersects = raycaster.intersectObjects(pointGroup.children);
                
                if (intersects.length > 0) {{
                    const hit = intersects[0].object;
                    if (hoveredPoint !== hit) {{
                        if (hoveredPoint) {{
                            hoveredPoint.scale.set(1, 1, 1);
                        }}
                        hoveredPoint = hit;
                        hoveredPoint.scale.set(1.6, 1.6, 1.6);
                        
                        const info = hoveredPoint.userData.info;
                        tooltip.style.opacity = 1;
                        tooltip.innerHTML = `
                            <strong>ID: ${{info.id}}</strong><br>
                            Mol Weight: ${{info.mw}} g/mol<br>
                            LogP: ${{info.logp}}<br>
                            Solubility: ${{info.solubility}} LogS<br>
                            Opt Score: ${{info.score}}
                        `;
                    }}
                }} else {{
                    if (hoveredPoint) {{
                        hoveredPoint.scale.set(1, 1, 1);
                        hoveredPoint = null;
                        tooltip.style.opacity = 0;
                    }}
                }}
                
                controls.update();
                renderer.render(scene, camera);
            }}
            
            animate();
            
            window.addEventListener('resize', () => {{
                camera.aspect = container.clientWidth / container.clientHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(container.clientWidth, container.clientHeight);
            }});
        </script>
    </body>
    </html>
    """
    components.html(html, height=380)

def render_3d_candidate_gallery(candidates: list, theme: str):
    """
    Renders rotating 3D candidate cards.
    """
    colors = get_theme_colors(theme)
    # Take top 6
    gal_data = []
    import hashlib
    for idx, c in enumerate(candidates[:6]):
        cid = c.get('candidate_id', f'Cand-{idx}')
        score = c.get('optimization_score', 50)
        be = c.get('binding_energy', -6.0)
        status = c.get('status', 'Active')
        
        gal_data.append({
            "id": cid,
            "score": score,
            "energy": be,
            "status": status,
            "rank": idx + 1
        })
    gal_json = json.dumps(gal_data)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                margin: 0;
                overflow: hidden;
                background-color: {colors["bg"]};
                font-family: 'Inter', sans-serif;
            }}
            #container {{
                width: 100vw;
                height: 400px;
                position: relative;
            }}
            #card-overlay {{
                position: absolute;
                bottom: 12px;
                left: 50%;
                transform: translateX(-50%);
                background: {colors["card_bg"]};
                border: 1px solid {colors["border"]};
                color: {colors["text"]};
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 13px;
                text-align: center;
                pointer-events: none;
                box-shadow: 0 4px 20px rgba(0,0,0,0.25);
            }}
        </style>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&family=Hanken+Grotesk:wght@800&display=swap" rel="stylesheet">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    </head>
    <body>
        <div id="container">
            <div id="card-overlay">Click/Rotate Cards</div>
        </div>
        
        <script>
            const data = {gal_json};
            const theme = "{theme}";
            const colors = {json.dumps(colors)};
            const container = document.getElementById('container');
            const overlay = document.getElementById('card-overlay');
            
            let scene, camera, renderer, controls, raycaster;
            const cards = [];
            const carouselRadius = 2.4;
            const cardGeometry = new THREE.PlaneGeometry(1.6, 2.0);
            let selectedMesh = null;
            const mouse = new THREE.Vector2();
            
            function createCardTexture(item) {{
                const canvas = document.createElement('canvas');
                canvas.width = 320;
                canvas.height = 400;
                const ctx = canvas.getContext('2d');
                
                // Background
                ctx.fillStyle = theme === 'dark' ? '#111827' : '#ffffff';
                ctx.beginPath();
                ctx.roundRect(0, 0, 320, 400, 20);
                ctx.fill();
                
                // Accent border
                ctx.strokeStyle = item.rank === 1 ? '#A855F7' : (item.rank === 2 ? '#3B82F6' : '#00687a');
                ctx.lineWidth = 8;
                ctx.stroke();
                
                // Title
                ctx.fillStyle = theme === 'dark' ? '#94a3b8' : '#4b5563';
                ctx.font = 'bold 16px Inter, sans-serif';
                ctx.fillText(`CANDIDATE RANK #${{item.rank}}`, 30, 60);
                
                // ID
                ctx.fillStyle = theme === 'dark' ? '#f8fafc' : '#0b1c30';
                ctx.font = '800 24px Hanken Grotesk, sans-serif';
                ctx.fillText(item.id, 30, 100);
                
                // Score
                ctx.fillStyle = '#00687a';
                ctx.font = '800 48px Hanken Grotesk, sans-serif';
                ctx.fillText(`${{item.score}}%`, 30, 190);
                ctx.fillStyle = theme === 'dark' ? '#94a3b8' : '#64748b';
                ctx.font = '12px Inter, sans-serif';
                ctx.fillText('OPTIMIZATION SCORE', 30, 220);
                
                // Energy
                ctx.fillStyle = theme === 'dark' ? '#f8fafc' : '#0b1c30';
                ctx.font = 'bold 20px Inter, sans-serif';
                ctx.fillText(`${{item.energy}} kcal/mol`, 30, 290);
                ctx.fillStyle = theme === 'dark' ? '#94a3b8' : '#64748b';
                ctx.font = '12px Inter, sans-serif';
                ctx.fillText('BINDING AFFINITY', 30, 310);
                
                // Status
                ctx.fillStyle = item.status === 'Completed' || item.status === 'Active' ? '#2ca02c' : '#f59e0b';
                ctx.beginPath();
                ctx.arc(36, 360, 6, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = theme === 'dark' ? '#94a3b8' : '#64748b';
                ctx.font = 'bold 12px Inter, sans-serif';
                ctx.fillText(item.status.toUpperCase(), 50, 364);
                
                return new THREE.CanvasTexture(canvas);
            }}
            
            function init() {{
                scene = new THREE.Scene();
                camera = new THREE.PerspectiveCamera(40, container.clientWidth / container.clientHeight, 0.1, 1000);
                camera.position.set(0, 0, 7.5);
                
                renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
                renderer.setSize(container.clientWidth, container.clientHeight);
                renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
                container.appendChild(renderer.domElement);
                
                controls = new THREE.OrbitControls(camera, renderer.domElement);
                controls.enableDamping = true;
                controls.enableZoom = false; // keep focus on carousel
                
                scene.add(new THREE.AmbientLight(0xffffff, theme === 'dark' ? 0.3 : 0.7));
                const pLight = new THREE.PointLight(0xffffff, 1.5, 30);
                pLight.position.set(0, 0, 5);
                scene.add(pLight);
                
                data.forEach((item, index) => {{
                    const angle = (index / data.length) * Math.PI * 2;
                    const texture = createCardTexture(item);
                    const mat = new THREE.MeshStandardMaterial({{
                        map: texture,
                        side: THREE.DoubleSide,
                        roughness: 0.1,
                        metalness: 0.5
                    }});
                    
                    const mesh = new THREE.Mesh(cardGeometry, mat);
                    const x = Math.cos(angle) * carouselRadius;
                    const z = Math.sin(angle) * carouselRadius;
                    
                    mesh.position.set(x, 0, z);
                    mesh.rotation.y = -angle + Math.PI / 2;
                    
                    mesh.userData = {{
                        info: item,
                        angle: angle
                    }};
                    
                    scene.add(mesh);
                    cards.push(mesh);
                }});
                
                raycaster = new THREE.Raycaster();
                
                window.addEventListener('mousemove', (e) => {{
                    const rect = renderer.domElement.getBoundingClientRect();
                    mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
                    mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
                }});
                
                window.addEventListener('click', () => {{
                    raycaster.setFromCamera(mouse, camera);
                    const intersects = raycaster.intersectObjects(cards);
                    if (intersects.length > 0) {{
                        const hit = intersects[0].object;
                        // Rotate carousel to bring clicked card to front
                        selectedMesh = hit;
                        overlay.innerHTML = `<strong>${{hit.userData.info.id}}</strong> | Affinity: <span style="color:#A855F7">${{hit.userData.info.energy}}</span>`;
                    }}
                }});
                
                window.addEventListener('resize', () => {{
                    camera.aspect = container.clientWidth / container.clientHeight;
                    camera.updateProjectionMatrix();
                    renderer.setSize(container.clientWidth, container.clientHeight);
                }});
                
                animate();
            }}
            
            function animate() {{
                requestAnimationFrame(animate);
                
                const time = Date.now() * 0.0005;
                
                // Slow general rotation if nothing selected
                if (!selectedMesh) {{
                    cards.forEach(card => {{
                        const newAngle = card.userData.angle + time * 0.1;
                        card.position.x = Math.cos(newAngle) * carouselRadius;
                        card.position.z = Math.sin(newAngle) * carouselRadius;
                        card.rotation.y = -newAngle + Math.PI / 2;
                        
                        // hover/bounce effect
                        card.position.y = Math.sin(time * 2 + card.userData.angle) * 0.05;
                    }});
                }}
                
                controls.update();
                renderer.render(scene, camera);
            }}
            
            // Wait for Google Fonts to be ready before drawing textures
            document.fonts.ready.then(() => {{
                setTimeout(init, 50);
            }}).catch(err => {{
                console.warn("Font loader failed, initializing immediately:", err);
                init();
            }});
        </script>
    </body>
    </html>
    """
    components.html(html, height=400)

def render_3d_resource_network(kpi_data: dict, theme: str):
    """
    Renders 3D Resource Usage Platforms and Session Flow.
    """
    colors = get_theme_colors(theme)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                margin: 0;
                overflow: hidden;
                background-color: {colors["bg"]};
                font-family: 'Inter', sans-serif;
            }}
            #container {{
                width: 100vw;
                height: 420px;
                position: relative;
            }}
            #tooltip {{
                position: absolute;
                bottom: 12px;
                right: 12px;
                background: {colors["card_bg"]};
                border: 1px solid {colors["border"]};
                padding: 10px;
                border-radius: 6px;
                color: {colors["text"]};
                font-size: 11px;
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.3s ease;
            }}
        </style>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    </head>
    <body>
        <div id="container">
            <div id="tooltip">Platform Metrics</div>
        </div>
        
        <script>
            const theme = "{theme}";
            const colors = {json.dumps(colors)};
            const container = document.getElementById('container');
            const tooltip = document.getElementById('tooltip');
            
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
            camera.position.set(0, 5, 8);
            
            const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
            renderer.setSize(container.clientWidth, container.clientHeight);
            container.appendChild(renderer.domElement);
            
            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            
            scene.add(new THREE.AmbientLight(0xffffff, theme === 'dark' ? 0.3 : 0.7));
            const dLight = new THREE.DirectionalLight(0xffffff, 1.2);
            dLight.position.set(5, 10, 5);
            scene.add(dLight);
            
            // Platform Modules list
            const modules = [
                "Target Explorer", "AI Screening", "Molecular Docking",
                "Lead Optimization", "ADMET Prediction", "Experiments", "Reports"
            ];
            
            const platforms = [];
            const radius = 3.0;
            const geom = new THREE.CylinderGeometry(0.4, 0.45, 0.2, 32);
            
            // Main Center Platform (Database)
            const dbMat = new THREE.MeshStandardMaterial({{ color: '#312E81', roughness: 0.1, metalness: 0.8 }});
            const dbPlatform = new THREE.Mesh(geom, dbMat);
            dbPlatform.position.set(0, 0, 0);
            scene.add(dbPlatform);
            
            // Build peripheral platforms
            modules.forEach((mod, idx) => {{
                const angle = (idx / modules.length) * Math.PI * 2;
                const x = Math.cos(angle) * radius;
                const z = Math.sin(angle) * radius;
                
                const c = idx % 2 === 0 ? '#00687a' : '#A855F7';
                const mat = new THREE.MeshStandardMaterial({{
                    color: c,
                    roughness: 0.2,
                    metalness: 0.6,
                    emissive: c,
                    emissiveIntensity: 0.1
                }});
                
                const mesh = new THREE.Mesh(geom, mat);
                mesh.position.set(x, 0.2, z);
                mesh.userData = {{ name: mod, color: c }};
                
                scene.add(mesh);
                platforms.push(mesh);
                
                // Add tube connecting to database center
                const path = new THREE.LineCurve3(new THREE.Vector3(0,0,0), new THREE.Vector3(x, 0.2, z));
                const tube = new THREE.Mesh(
                    new THREE.TubeGeometry(path, 20, 0.03, 8, false),
                    new THREE.MeshBasicMaterial({{ color: colors.border, transparent: true, opacity: 0.15 }})
                );
                scene.add(tube);
            }});
            
            // Session Flow Particles traveling between platforms and center
            const particleCount = 28;
            const particleGeom = new THREE.SphereGeometry(0.05, 8, 8);
            const particleMat = new THREE.MeshBasicMaterial({{ color: '#ffffff' }});
            const particles = [];
            
            for (let i = 0; i < particleCount; i++) {{
                const p = new THREE.Mesh(particleGeom, particleMat);
                resetParticle(p);
                scene.add(p);
                particles.push(p);
            }}
            
            function resetParticle(p) {{
                const platform = platforms[Math.floor(Math.random() * platforms.length)];
                p.userData = {{
                    target: platform.position.clone(),
                    start: new THREE.Vector3(0, 0.1, 0),
                    t: Math.random(),
                    speed: 0.008 + Math.random() * 0.008,
                    outbound: Math.random() > 0.5
                }};
            }}
            
            // Raycast
            const raycaster = new THREE.Raycaster();
            const mouse = new THREE.Vector2();
            let hoveredPlatform = null;
            
            window.addEventListener('mousemove', (e) => {{
                const rect = renderer.domElement.getBoundingClientRect();
                mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
                mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
            }});
            
            function animate() {{
                requestAnimationFrame(animate);
                
                // Rotate center
                dbPlatform.rotation.y += 0.01;
                
                // Move particles
                particles.forEach(p => {{
                    p.userData.t += p.userData.speed;
                    if (p.userData.t >= 1.0) {{
                        resetParticle(p);
                    }} else {{
                        const t = p.userData.t;
                        if (p.userData.outbound) {{
                            p.position.lerpVectors(p.userData.start, p.userData.target, t);
                        }} else {{
                            p.position.lerpVectors(p.userData.target, p.userData.start, t);
                        }}
                    }}
                }});
                
                // Raycasting
                raycaster.setFromCamera(mouse, camera);
                const intersects = raycaster.intersectObjects(platforms);
                
                if (intersects.length > 0) {{
                    const hit = intersects[0].object;
                    if (hoveredPlatform !== hit) {{
                        if (hoveredPlatform) {{
                            hoveredPlatform.scale.set(1, 1, 1);
                            hoveredPlatform.material.emissiveIntensity = 0.1;
                        }}
                        hoveredPlatform = hit;
                        hoveredPlatform.scale.set(1.2, 1.2, 1.2);
                        hoveredPlatform.material.emissiveIntensity = 0.6;
                        
                        tooltip.style.opacity = 1;
                        tooltip.innerHTML = `<strong>${{hoveredPlatform.userData.name}}</strong>`;
                    }}
                }} else {{
                    if (hoveredPlatform) {{
                        hoveredPlatform.scale.set(1, 1, 1);
                        hoveredPlatform.material.emissiveIntensity = 0.1;
                        hoveredPlatform = null;
                        tooltip.style.opacity = 0;
                    }}
                }}
                
                controls.update();
                renderer.render(scene, camera);
            }}
            
            animate();
            
            window.addEventListener('resize', () => {{
                camera.aspect = container.clientWidth / container.clientHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(container.clientWidth, container.clientHeight);
            }});
        </script>
    </body>
    </html>
    """
    components.html(html, height=420)

def render_3d_knowledge_graph(theme: str):
    """
    Visualizes Target -> Screening -> Docking -> Optimization -> ADMET -> Candidate -> Report.
    """
    colors = get_theme_colors(theme)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                margin: 0;
                overflow: hidden;
                background-color: {colors["bg"]};
                font-family: 'Inter', sans-serif;
            }}
            #container {{
                width: 100vw;
                height: 380px;
                position: relative;
            }}
            #tooltip {{
                position: absolute;
                top: 12px;
                left: 12px;
                background: {colors["card_bg"]};
                border: 1px solid {colors["border"]};
                padding: 10px;
                border-radius: 6px;
                color: {colors["text"]};
                font-size: 11px;
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.3s ease;
                min-width: 160px;
            }}
        </style>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    </head>
    <body>
        <div id="container">
            <div id="tooltip">Node details</div>
        </div>
        
        <script>
            const theme = "{theme}";
            const colors = {json.dumps(colors)};
            const container = document.getElementById('container');
            const tooltip = document.getElementById('tooltip');
            
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(40, container.clientWidth / container.clientHeight, 0.1, 1000);
            camera.position.set(0, 0, 7);
            
            const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
            renderer.setSize(container.clientWidth, container.clientHeight);
            container.appendChild(renderer.domElement);
            
            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            
            scene.add(new THREE.AmbientLight(0xffffff, theme === 'dark' ? 0.3 : 0.7));
            const pLight = new THREE.PointLight(0xffffff, 1.2, 30);
            pLight.position.set(0, 5, 5);
            scene.add(pLight);
            
            // Define Nodes
            const graphNodes = [
                {{ name: "Target", desc: "Disease-related protein receptors", x: -3.0, y: 0.5, color: "#3B82F6" }},
                {{ name: "Screening", desc: "High-throughput molecular scoring", x: -2.0, y: -0.5, color: "#06B6D4" }},
                {{ name: "Docking", desc: "Atomic orientation & binding binding energy", x: -1.0, y: 0.5, color: "#00687a" }},
                {{ name: "Optimization", desc: "Chemical scaffold refinement", x: 0.0, y: -0.5, color: "#A855F7" }},
                {{ name: "ADMET", desc: "Absorption & toxicity profiling", x: 1.0, y: 0.5, color: "#EC4899" }},
                {{ name: "Candidate", desc: "Prioritized clinical drug assets", x: 2.0, y: -0.5, color: "#10B981" }},
                {{ name: "Report", desc: "Compliance & synthesis dossiers", x: 3.0, y: 0.5, color: "#F59E0B" }}
            ];
            
            const nodeGeom = new THREE.SphereGeometry(0.18, 32, 32);
            const meshes = [];
            
            graphNodes.forEach((node, idx) => {{
                const mat = new THREE.MeshStandardMaterial({{
                    color: node.color,
                    roughness: 0.1,
                    metalness: 0.7,
                    emissive: node.color,
                    emissiveIntensity: 0.15
                }});
                const mesh = new THREE.Mesh(nodeGeom, mat);
                mesh.position.set(node.x, node.y, 0);
                mesh.userData = {{ info: node }};
                scene.add(mesh);
                mesh.userData = {{ info: node }};
                meshes.push(mesh);
                
                // Add connector to next
                if (idx < graphNodes.length - 1) {{
                    const next = graphNodes[idx + 1];
                    const pts = [new THREE.Vector3(node.x, node.y, 0), new THREE.Vector3(next.x, next.y, 0)];
                    const path = new THREE.CatmullRomCurve3(pts);
                    
                    const tube = new THREE.Mesh(
                        new THREE.TubeGeometry(path, 10, 0.03, 8, false),
                        new THREE.MeshStandardMaterial({{ color: colors.border, roughness: 0.5 }})
                    );
                    scene.add(tube);
                }}
            }});
            
            // Raycast
            const raycaster = new THREE.Raycaster();
            const mouse = new THREE.Vector2();
            let hoveredNode = null;
            
            window.addEventListener('mousemove', (e) => {{
                const rect = renderer.domElement.getBoundingClientRect();
                mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
                mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
            }});
            
            function animate() {{
                requestAnimationFrame(animate);
                
                // Gentle rotation
                scene.rotation.y = Math.sin(Date.now() * 0.0002) * 0.1;
                
                raycaster.setFromCamera(mouse, camera);
                const intersects = raycaster.intersectObjects(meshes);
                
                if (intersects.length > 0) {{
                    const hit = intersects[0].object;
                    if (hoveredNode !== hit) {{
                        if (hoveredNode) {{
                            hoveredNode.scale.set(1, 1, 1);
                            hoveredNode.material.emissiveIntensity = 0.15;
                        }}
                        hoveredNode = hit;
                        hoveredNode.scale.set(1.4, 1.4, 1.4);
                        hoveredNode.material.emissiveIntensity = 0.6;
                        
                        const info = hoveredNode.userData.info;
                        tooltip.style.opacity = 1;
                        tooltip.innerHTML = `
                            <strong style="color:${{info.color}}">${{info.name}}</strong><br>
                            ${{info.desc}}
                        `;
                    }}
                }} else {{
                    if (hoveredNode) {{
                        hoveredNode.scale.set(1, 1, 1);
                        hoveredNode.material.emissiveIntensity = 0.15;
                        hoveredNode = null;
                        tooltip.style.opacity = 0;
                    }}
                }}
                
                controls.update();
                renderer.render(scene, camera);
            }}
            
            animate();
            
            window.addEventListener('resize', () => {{
                camera.aspect = container.clientWidth / container.clientHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(container.clientWidth, container.clientHeight);
            }});
        </script>
    </body>
    </html>
    """
    components.html(html, height=380)
