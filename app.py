import os
import json
import streamlit as st
import streamlit.components.v1 as components

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Fluxo de Fechamento — Controladoria",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────
# 1. IDENTIDADE VISUAL PREMIUM (PALETA EXECUTIVA MINIMALISTA)
# ─────────────────────────────────────────────────────────────
COLOR_PALETTE = {
    "1": {"name": "CONCILIAÇÃO E RESULTADO", "main": "#475569", "bg": "#f8fafc", "border": "#cbd5e1", "text": "#1e293b"},
    "2": {"name": "ANÁLISE FINAL",           "main": "#d97706", "bg": "#fffbeb", "border": "#fde68a", "text": "#78350f"},
    "3": {"name": "APURAÇÃO DE POCs",        "main": "#16a34a", "bg": "#f0fdf4", "border": "#bbf7d0", "text": "#14532d"},
    "4": {"name": "CONFERÊNCIAS NOMINAIS",   "main": "#dc2626", "bg": "#fef2f2", "border": "#fecaca", "text": "#7f1d1d"},
    "5": {"name": "BASES DE ORÇAMENTO",      "main": "#2563eb", "bg": "#eff6ff", "border": "#bfdbfe", "text": "#1e3a8a"},
    "6": {"name": "GATILHOS",                "main": "#7c3aed", "bg": "#f5f3ff", "border": "#ddd6fe", "text": "#4c1d95"},
}

SKIP_GROUP_IDS = {"4392351365515c6d", "6283cfcedbf60137"}

def clean_label(raw: str) -> str:
    text = raw.replace("[[", "").replace("]]", "")
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if not lines: return raw
    first = lines[0]
    if "/" in first and len(first) > 35:
        first = first.split("/")[-1]
    return first

def wrap_text(text, max_chars=30):
    words = text.split()
    lines = []
    current_line = []
    current_length = 0
    for word in words:
        if current_length + len(word) <= max_chars:
            current_line.append(word)
            current_length += len(word) + 1
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
            current_length = len(word) + 1
    if current_line:
        lines.append(" ".join(current_line))
    return lines[:3]

# ─────────────────────────────────────────────────────────────
# 2. GERAÇÃO DE CARDS PREMIUM VIA SVG (VETORIAL)
# ─────────────────────────────────────────────────────────────
def create_svg_card(title, subtitle, palette_item, is_active=False):
    title_lines = wrap_text(title, max_chars=26)
    
    y_start = 45 if len(title_lines) == 1 else (38 if len(title_lines) == 2 else 32)
    text_svg = ""
    for i, line in enumerate(title_lines):
        text_svg += f'<text x="25" y="{y_start + (i * 18)}" font-family="Inter, Segoe UI, sans-serif" font-size="13" font-weight="700" fill="{palette_item["text"]}">{line}</text>'
    
    sub_text = subtitle.replace(title, "").strip()[:40]
    if sub_text:
        sub_text = sub_text + "..." if len(sub_text) >= 40 else sub_text
        text_svg += f'<text x="25" y="92" font-family="Inter, Segoe UI, sans-serif" font-size="10" fill="#64748b">{sub_text}</text>'

    stroke_color = "#2563eb" if is_active else palette_item["border"]
    stroke_width = "3" if is_active else "1"
    shadow_opacity = "0.25" if is_active else "0.08"
    shadow_blur = "10" if is_active else "5"

    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="260" height="110">
        <defs>
            <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%">
                <feDropShadow dx="0" dy="4" stdDeviation="{shadow_blur}" flood-color="#0f172a" flood-opacity="{shadow_opacity}"/>
            </filter>
        </defs>
        <rect x="5" y="5" width="245" height="100" rx="10" fill="{palette_item["bg"]}" stroke="{stroke_color}" stroke-width="{stroke_width}" filter="url(#shadow)" />
        <path d="M 5 15 A 10 10 0 0 1 15 5 L 15 5 L 15 105 L 15 105 A 10 10 0 0 1 5 95 Z" fill="{palette_item["main"]}" />
        {text_svg}
    </svg>
    """
    import base64
    b64 = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
    return f"data:image/svg+xml;base64,{b64}"

# ─────────────────────────────────────────────────────────────
# 3. CARREGAMENTO E MAPEAMENTO DE DADOS
# ─────────────────────────────────────────────────────────────
@st.cache_data
def load_canvas_data(filename="FLUXO_FINAL.canvas"):
    if not os.path.exists(filename):
        return [], [], {}
    
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    raw_nodes = data.get("nodes", [])
    raw_edges = data.get("edges", [])
    
    nodes_map = {}
    vis_nodes = []
    vis_edges = []
    
    for n in raw_nodes:
        if n.get("type") == "text" and n["id"] not in SKIP_GROUP_IDS:
            color_key = n.get("color", "1")
            full_text = n.get("text", "").replace("[[", "").replace("]]", "")
            label = clean_label(full_text)
            
            nodes_map[n["id"]] = {
                "id": n["id"],
                "label": label,
                "full_text": full_text,
                "color_key": color_key,
                "x": n["x"],
                "y": n["y"]
            }
            
    for e in raw_edges:
        if e["fromNode"] in nodes_map and e["toNode"] in nodes_map:
            color_key = e.get("color", "1")
            palette = COLOR_PALETTE.get(color_key, COLOR_PALETTE["1"])
            vis_edges.append({
                "id": e["id"],
                "from": e["fromNode"],
                "to": e["toNode"],
                "arrows": {"to": {"enabled": True, "type": "arrow"}},
                "color": {"color": palette["main"], "opacity": 0.35, "highlight": "#2563eb", "hover": "#2563eb"},
                "width": 1.5,
                "smooth": {"type": "cubicBezier", "roundness": 0.5}
            })
            
    return vis_nodes, vis_edges, nodes_map

_, vis_edges, nodes_map = load_canvas_data()

def get_lineage(active_id, edges):
    upstream_nodes, downstream_nodes = set(), set()
    
    def trace_up(nid):
        for e in edges:
            if e["to"] == nid and e["from"] not in upstream_nodes:
                upstream_nodes.add(e["from"])
                trace_up(e["from"])
                
    def trace_down(nid):
        for e in edges:
            if e["from"] == nid and e["to"] not in downstream_nodes:
                downstream_nodes.add(e["to"])
                trace_down(e["to"])
                
    if active_id:
        trace_up(active_id)
        trace_down(active_id)
        
    return list(upstream_nodes), list(downstream_nodes)

# ─────────────────────────────────────────────────────────────
# 4. INTERFACE E SIDEBAR EXECUTIVA
# ─────────────────────────────────────────────────────────────
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        .block-container { padding-top: 1.5rem; background-color: #f8fafc; font-family: 'Inter', sans-serif; }
        .stSelectbox label { font-size: 11px !important; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }
        div[data-testid="stSidebarUserContent"] { background-color: #ffffff; padding: 1.5rem 1rem; }
        .metric-card { background: #f1f5f9; padding: 10px; border-radius: 6px; text-align: center; border: 1px solid #e2e8f0; }
        .metric-val { font-size: 18px; font-weight: 700; color: #0f172a; }
        .metric-lbl { font-size: 10px; color: #64748b; text-transform: uppercase; }
    </style>
""", unsafe_allow_html=True)

st.markdown("### Arquitetura de Processos <span style='font-size:15px; color:#64748b; font-weight:normal;'>— Controladoria Premium</span>", unsafe_allow_html=True)

legenda_html = "".join([
    f"<span style='display:inline-block; margin-right:8px; margin-bottom:6px; padding:4px 12px; border-radius:6px; font-size:11px; font-weight:600; background:{v['bg']}; border:1px solid {v['border']}; color:{v['text']};'><span style='color:{v['main']}; margin-right:4px;'>■</span> {v['name']}</span>"
    for k, v in COLOR_PALETTE.items()
])
st.markdown(f"<div style='margin-bottom:20px;'>{legenda_html}</div>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h2 style='font-size:18px; font-weight:700; color:#0f172a; margin-bottom:15px;'>⇄ Navegação</h2>", unsafe_allow_html=True)
    
    search_options = {v["label"]: k for k, v in nodes_map.items()}
    selected_label = st.selectbox("Filtro de Processo Focal:", [""] + list(search_options.keys()))
    active_id = search_options.get(selected_label, None)
    
    filter_mode = st.radio(
        "Isolamento de Linhagem:",
        ["⟷ Cadeia Integrada (Ambos)", "← Origens Analíticas (Upstream)", "→ Impactos Operacionais (Downstream)"],
        index=0
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if active_id:
        node_info = nodes_map[active_id]
        palette = COLOR_PALETTE[node_info["color_key"]]
        up_nodes, down_nodes = get_lineage(active_id, vis_edges)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"<div class='metric-card'><div class='metric-val'>{len(up_nodes)}</div><div class='metric-lbl'>Origens</div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='metric-card'><div class='metric-val'>{len(down_nodes)}</div><div class='metric-lbl'>Impactados</div></div>", unsafe_allow_html=True)
            
        st.markdown(f"""
            <div style="background-color: {palette['bg']}; border: 1px solid {palette['border']}; border-left: 4px solid {palette['main']}; border-radius: 6px; padding: 14px; margin-top: 15px;">
                <div style="font-size: 10px; font-weight: 700; color: {palette['main']}; text-transform: uppercase; margin-bottom:4px;">Documentação do Nó</div>
                <div style="font-size: 14px; font-weight: 700; color: {palette['text']};">{node_info['label']}</div>
                <div style="font-size: 12px; color: #475569; margin-top: 8px; line-height: 1.4; white-space: pre-wrap;">{node_info['full_text']}</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info("💡 Escolha uma etapa para analisar as conexões de entrada/saída e isolar dependências críticas.")

# ─────────────────────────────────────────────────────────────
# 5. RECONSTRUÇÃO DOS NÓS COM IMAGENS SVG DINÂMICAS
# ─────────────────────────────────────────────────────────────
final_vis_nodes = []
up_nodes, down_nodes = get_lineage(active_id, vis_edges) if active_id else ([], [])

for nid, n in nodes_map.items():
    palette = COLOR_PALETTE[n["color_key"]]
    is_focal = (nid == active_id)
    
    if active_id:
        show_up = ("Integrada" in filter_mode or "Origens" in filter_mode) and nid in up_nodes
        show_down = ("Integrada" in filter_mode or "Impactos" in filter_mode) and nid in down_nodes
        if not (is_focal or show_up or show_down):
            final_vis_nodes.append({
                "id": nid, "x": n["x"], "y": n["y"], "shape": "image",
                "image": create_svg_card(n["label"], n["full_text"], palette, is_active=False),
                "opacity": 0.12, "fixed": True
            })
            continue

    img_url = create_svg_card(n["label"], n["full_text"], palette, is_active=is_focal)
    final_vis_nodes.append({
        "id": nid, "x": n["x"], "y": n["y"], "shape": "image", "image": img_url, "opacity": 1.0, "fixed": True
    })

final_vis_edges = []
for e in vis_edges:
    edge_copy = dict(e)
    if active_id:
        is_up_edge = edge_copy["to"] == active_id or (edge_copy["to"] in up_nodes and edge_copy["from"] in up_nodes)
        is_down_edge = edge_copy["from"] == active_id or (edge_copy["from"] in down_nodes and edge_copy["to"] in down_nodes)
        
        if ("Integrada" in filter_mode and (is_up_edge or is_down_edge)) or \
           ("Origens" in filter_mode and is_up_edge) or \
           ("Impactos" in filter_mode and is_down_edge):
            edge_copy["width"] = 2.5
            edge_copy["color"] = {"color": "#2563eb", "opacity": 0.85}
            edge_copy["arrows"] = {"to": {"enabled": True, "scaleFactor": 1.2}}
        else:
            edge_copy["color"] = {"opacity": 0.04}
    final_vis_edges.append(edge_copy)

# ─────────────────────────────────────────────────────────────
# 6. COMPONENTE INJETADO COM GRID CONFIGURADO (ESTILO FIGMA)
# ─────────────────────────────────────────────────────────────
html_source = f"""
<!DOCTYPE html>
<html>
<head>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style type="text/css">
        #network-canvas {{ 
            width: 100%; 
            height: 76vh; 
            background-color: #f8fafc; 
            background-image: radial-gradient(#cbd5e1 1px, transparent 1px);
            background-size: 24px 24px;
            border: 1px solid #e2e8f0; 
            border-radius: 12px; 
        }}
    </style>
</head>
<body>
    <div id="network-canvas"></div>
    <script type="text/javascript">
        var container = document.getElementById('network-canvas');
        var data = {{
            nodes: new vis.DataSet({json.dumps(final_vis_nodes)}),
            edges: new vis.DataSet({json.dumps(final_vis_edges)})
        }};
        var options = {{
            physics: {{ enabled: false }},
            interaction: {{ 
                dragNodes: false, 
                zoomView: true, 
                dragView: true,
                hover: true
            }},
            nodes: {{
                useBorderWithImage: false
            }}
        }};
        var network = new vis.Network(container, data, options);
    </script>
</body>
</html>
"""

components.html(html_source, height=620)
st.caption("⚙️ Controles de Tela: Use a rolagem do mouse para dar zoom. Clique e arraste na malha de pontos para navegar.")
