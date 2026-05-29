"""
Fluxo de Fechamento — Controladoria Codeme
Dashboard de Inteligência Operacional Premium
"""

import os
import json
import base64
import streamlit as st
import streamlit.components.v1 as components

# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURAÇÃO INICIAL DA PÁGINA
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Controladoria — Inteligência Operacional",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "Sistema de Inteligência Operacional — Controladoria Codeme"
    }
)

# ──────────────────────────────────────────────────────────────────────────────
# PALETA DE CORES E METADADOS DAS MACROETAPAS
# ──────────────────────────────────────────────────────────────────────────────
PALETTE = {
    "1": {"name": "Conciliação & Resultado", "icon": "◈", "main": "#64748b", "bg": "#f8fafc", "border": "#cbd5e1", "text": "#1e293b", "accent": "#475569"},
    "2": {"name": "Análise Final",            "icon": "◆", "main": "#b45309", "bg": "#fffbeb", "border": "#fcd34d", "text": "#78350f", "accent": "#d97706"},
    "3": {"name": "Apuração de POCs",         "icon": "◉", "main": "#15803d", "bg": "#f0fdf4", "border": "#86efac", "text": "#14532d", "accent": "#16a34a"},
    "4": {"name": "Conferências Nominais",    "icon": "◎", "main": "#b91c1c", "bg": "#fef2f2", "border": "#fca5a5", "text": "#7f1d1d", "accent": "#dc2626"},
    "5": {"name": "Bases de Orçamento",       "icon": "◇", "main": "#1d4ed8", "bg": "#eff6ff", "border": "#93c5fd", "text": "#1e3a8a", "accent": "#2563eb"},
    "6": {"name": "Gatilhos",                 "icon": "◈", "main": "#6d28d9", "bg": "#f5f3ff", "border": "#c4b5fd", "text": "#4c1d95", "accent": "#7c3aed"},
}

SKIP_IDS = {"4392351365515c6d", "6283cfcedbf60137"}

# Ordem lógica das macroetapas para o pipeline view
PIPELINE_ORDER = ["6", "4", "3", "5", "1", "2"]

# ──────────────────────────────────────────────────────────────────────────────
# CSS GLOBAL — DESIGN SYSTEM EXECUTIVO
# ──────────────────────────────────────────────────────────────────────────────
def inject_global_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');

    /* ── RESET & BASE ── */
    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif !important;
    }
    .block-container {
        padding: 1.5rem 2rem 2rem 2rem !important;
        max-width: 100% !important;
        background: #f1f5f9;
    }
    #MainMenu, footer, header { visibility: hidden; }

    /* ── SIDEBAR ── */
    [data-testid="stSidebar"] {
        background: #0f172a !important;
        border-right: 1px solid #1e293b;
    }
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stRadio label {
        font-size: 10px !important;
        font-weight: 700 !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
        color: #64748b !important;
    }
    [data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
        color: #e2e8f0 !important;
        border-radius: 6px !important;
    }
    [data-testid="stSidebar"] [data-testid="stSelectbox"] svg {
        color: #94a3b8 !important;
    }
    [data-testid="stSidebar"] .stRadio > div {
        gap: 6px !important;
    }
    [data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
        font-size: 12px !important;
        font-weight: 500 !important;
        color: #cbd5e1 !important;
    }

    /* ── TABS ── */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        border-bottom: 1px solid #e2e8f0;
        gap: 0;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        letter-spacing: 0.8px !important;
        text-transform: uppercase !important;
        color: #64748b !important;
        background: transparent !important;
        border: none !important;
        border-bottom: 3px solid transparent !important;
        padding: 10px 20px !important;
        transition: all 0.2s ease !important;
    }
    .stTabs [aria-selected="true"] {
        color: #0f172a !important;
        border-bottom: 3px solid #0f172a !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding: 0 !important;
    }

    /* ── METRIC CARDS ── */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin-bottom: 16px;
    }
    .metric-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 14px 16px;
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: var(--accent);
    }
    .metric-val {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 28px;
        font-weight: 600;
        color: #0f172a;
        line-height: 1;
        margin-bottom: 4px;
    }
    .metric-lbl {
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        color: #94a3b8;
    }
    .metric-sub {
        font-size: 11px;
        color: #64748b;
        margin-top: 4px;
    }

    /* ── NODE DETAIL CARD ── */
    .node-detail {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 20px;
        margin-top: 12px;
    }
    .node-detail-header {
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #94a3b8;
        margin-bottom: 6px;
    }
    .node-detail-title {
        font-size: 16px;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 12px;
        border-left: 3px solid var(--accent-color, #0f172a);
        padding-left: 10px;
    }
    .node-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-right: 6px;
        margin-bottom: 4px;
    }
    .dependency-list {
        background: #f8fafc;
        border-radius: 6px;
        padding: 10px 14px;
        margin-top: 8px;
    }
    .dependency-item {
        font-size: 12px;
        color: #475569;
        padding: 4px 0;
        border-bottom: 1px solid #f1f5f9;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .dependency-item:last-child { border-bottom: none; }

    /* ── PIPELINE TABLE ── */
    .pipeline-row {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 14px;
        border-radius: 6px;
        margin-bottom: 4px;
        background: white;
        border: 1px solid #f1f5f9;
        transition: all 0.15s ease;
    }
    .pipeline-row:hover {
        border-color: #e2e8f0;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    .pipeline-icon {
        font-size: 16px;
        width: 24px;
        text-align: center;
    }
    .pipeline-name {
        font-size: 13px;
        font-weight: 600;
        color: #1e293b;
        flex: 1;
    }
    .pipeline-count {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
        color: #94a3b8;
        background: #f1f5f9;
        padding: 2px 8px;
        border-radius: 4px;
    }

    /* ── SEARCH HIGHLIGHT ── */
    .search-result {
        background: #fffbeb;
        border: 1px solid #fcd34d;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 6px;
        cursor: pointer;
    }
    .search-result-name {
        font-size: 13px;
        font-weight: 600;
        color: #1e293b;
    }
    .search-result-type {
        font-size: 10px;
        color: #92400e;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* ── CANVAS CONTAINER ── */
    .canvas-wrapper {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    /* ── STCARD OVERRIDES ── */
    div[data-testid="column"] { gap: 12px; }

    /* ── DIVIDER ── */
    .section-divider {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 20px 0 14px;
    }
    .section-divider-label {
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #94a3b8;
        white-space: nowrap;
    }
    .section-divider-line {
        flex: 1;
        height: 1px;
        background: #e2e8f0;
    }

    /* ── SCROLLBAR ── */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# FUNÇÕES UTILITÁRIAS
# ──────────────────────────────────────────────────────────────────────────────
def clean_label(raw: str) -> str:
    text = raw.replace("[[", "").replace("]]", "").strip()
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if not lines:
        return raw
    first = lines[0]
    if "/" in first:
        first = first.split("/")[-1]
    return first[:60]


def wrap_text(text, max_chars=25):
    words = text.split()
    lines, current_line, current_len = [], [], 0
    for word in words:
        if current_len + len(word) + 1 <= max_chars:
            current_line.append(word)
            current_len += len(word) + 1
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line, current_len = [word], len(word)
    if current_line:
        lines.append(" ".join(current_line))
    return lines[:3]


def svg_to_b64(svg: str) -> str:
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("utf-8")


def create_node_svg(title: str, palette: dict, state: str = "normal") -> str:
    """
    state: 'normal' | 'focal' | 'upstream' | 'downstream' | 'dimmed'
    """
    lines = wrap_text(title, 24)
    y0 = 44 if len(lines) == 1 else (36 if len(lines) == 2 else 28)
    
    text_svg = "".join(
        f'<text x="24" y="{y0 + i*17}" font-family="IBM Plex Sans,sans-serif" '
        f'font-size="12" font-weight="600" fill="{palette["text"]}">{l}</text>'
        for i, l in enumerate(lines)
    )

    if state == "focal":
        stroke, sw, opacity, shadow_op = "#0f172a", "2.5", "1", "0.18"
    elif state == "upstream":
        stroke, sw, opacity, shadow_op = "#7c3aed", "1.5", "1", "0.10"
    elif state == "downstream":
        stroke, sw, opacity, shadow_op = "#15803d", "1.5", "1", "0.10"
    elif state == "dimmed":
        stroke, sw, opacity, shadow_op = palette["border"], "1", "0.18", "0"
    else:
        stroke, sw, opacity, shadow_op = palette["border"], "1", "1", "0.07"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="250" height="95">
  <defs>
    <filter id="s"><feDropShadow dx="0" dy="3" stdDeviation="5" flood-color="#0f172a" flood-opacity="{shadow_op}"/></filter>
  </defs>
  <rect x="4" y="4" width="236" height="83" rx="8"
    fill="{palette['bg']}" stroke="{stroke}" stroke-width="{sw}"
    filter="url(#s)" opacity="{opacity}"/>
  <rect x="4" y="4" width="8" height="83"
    rx="4" fill="{palette['main']}" opacity="{opacity}"/>
  {text_svg}
</svg>"""
    return svg_to_b64(svg)


# ──────────────────────────────────────────────────────────────────────────────
# CARREGAMENTO E PROCESSAMENTO DOS DADOS DO CANVAS
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_canvas(path: str = "FLUXO_FINAL.canvas"):
    if not os.path.exists(path):
        return {}, [], {}
    
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    nodes_map: dict[str, dict] = {}
    edges_raw = raw.get("edges", [])

    for n in raw.get("nodes", []):
        if n.get("type") != "text" or n["id"] in SKIP_IDS:
            continue
        color_key = str(n.get("color", "1"))
        full_text = n.get("text", "")
        label = clean_label(full_text)
        nodes_map[n["id"]] = {
            "id": n["id"],
            "label": label,
            "full_text": full_text.replace("[[", "").replace("]]", "").strip(),
            "color_key": color_key,
            "x": n.get("x", 0),
            "y": n.get("y", 0),
            "w": n.get("width", 250),
            "h": n.get("height", 60),
        }

    edges = [
        e for e in edges_raw
        if e.get("fromNode") in nodes_map and e.get("toNode") in nodes_map
    ]
    
    # Pré-calcular adjacências para análise rápida
    adj: dict[str, dict] = {nid: {"in": [], "out": []} for nid in nodes_map}
    for e in edges:
        adj[e["fromNode"]]["out"].append(e["toNode"])
        adj[e["toNode"]]["in"].append(e["fromNode"])

    return nodes_map, edges, adj


@st.cache_data(show_spinner=False)
def compute_metrics(nodes_map: dict, edges: list, adj: dict) -> dict:
    """Computa métricas operacionais do grafo."""
    n_total = len(nodes_map)
    n_edges = len(edges)

    # Nós por macroetapa
    by_stage: dict[str, list] = {k: [] for k in PALETTE}
    for nid, nd in nodes_map.items():
        by_stage.setdefault(nd["color_key"], []).append(nid)

    # Nós críticos: alto grau de entrada OU saída
    criticality = {
        nid: len(adj[nid]["in"]) + len(adj[nid]["out"])
        for nid in nodes_map
    }
    top5 = sorted(criticality.items(), key=lambda x: -x[1])[:5]

    # Gatilhos (color_key == "6") e seus impactos
    gatilhos = [nid for nid, nd in nodes_map.items() if nd["color_key"] == "6"]

    return {
        "n_total": n_total,
        "n_edges": n_edges,
        "by_stage": by_stage,
        "criticality": criticality,
        "top5": top5,
        "gatilhos": gatilhos,
    }


def get_lineage(nid: str, adj: dict) -> tuple[set, set]:
    """BFS bidirecional para obter ancestrais e descendentes."""
    def bfs(start_list, direction):
        visited = set()
        queue = list(start_list)
        while queue:
            current = queue.pop(0)
            for neighbor in adj.get(current, {}).get(direction, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return visited

    upstream = bfs(adj[nid]["in"], "in")
    downstream = bfs(adj[nid]["out"], "out")
    return upstream, downstream


# ──────────────────────────────────────────────────────────────────────────────
# COMPONENTE DO GRAFO (vis.js) — VERSÃO AVANÇADA
# ──────────────────────────────────────────────────────────────────────────────
def build_graph_html(
    nodes_map: dict,
    edges: list,
    adj: dict,
    active_id: str | None = None,
    filter_mode: str = "both",
    height: int = 640,
) -> str:
    
    upstream, downstream = (get_lineage(active_id, adj) if active_id else (set(), set()))
    
    # Montar nós
    vis_nodes = []
    for nid, nd in nodes_map.items():
        palette = PALETTE[nd["color_key"]]

        if active_id:
            if nid == active_id:
                state = "focal"
            elif nid in upstream and filter_mode in ("both", "up"):
                state = "upstream"
            elif nid in downstream and filter_mode in ("both", "down"):
                state = "downstream"
            else:
                state = "dimmed"
        else:
            state = "normal"

        vis_nodes.append({
            "id": nid,
            "x": nd["x"],
            "y": nd["y"],
            "shape": "image",
            "image": create_node_svg(nd["label"], palette, state),
            "size": 125,
            "opacity": 0.15 if state == "dimmed" else 1.0,
            "fixed": {"x": True, "y": True},
            "title": nd["label"],
        })

    # Montar arestas
    vis_edges = []
    for e in edges:
        ck = str(e.get("color", "1"))
        palette = PALETTE.get(ck, PALETTE["1"])
        
        from_n, to_n = e["fromNode"], e["toNode"]
        
        if active_id:
            is_up = (to_n == active_id and from_n in upstream) or \
                    (from_n in upstream and to_n in upstream) or \
                    (to_n == active_id)
            is_down = (from_n == active_id and to_n in downstream) or \
                      (from_n in downstream and to_n in downstream) or \
                      (from_n == active_id)
            
            if (filter_mode in ("both", "up") and is_up) or \
               (filter_mode in ("both", "down") and is_down):
                edge_color = {"color": "#2563eb", "opacity": 0.9}
                edge_width = 2.5
            else:
                edge_color = {"color": "#94a3b8", "opacity": 0.05}
                edge_width = 1
        else:
            edge_color = {"color": palette["main"], "opacity": 0.3, "highlight": "#2563eb"}
            edge_width = 1.5

        vis_edges.append({
            "id": e["id"],
            "from": from_n,
            "to": to_n,
            "color": edge_color,
            "width": edge_width,
            "arrows": {"to": {"enabled": True, "scaleFactor": 0.7}},
            "smooth": {"type": "cubicBezier", "roundness": 0.4, "forceDirection": "horizontal"},
        })

    nodes_json = json.dumps(vis_nodes)
    edges_json = json.dumps(vis_edges)

    return f"""<!DOCTYPE html><html><head>
<script src="https://unpkg.com/vis-network@9.1.9/standalone/umd/vis-network.min.js"></script>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:#f8fafc; }}
  #net {{
    width:100%; height:{height}px;
    background-color: #f8fafc;
    background-image:
      linear-gradient(rgba(148,163,184,0.15) 1px, transparent 1px),
      linear-gradient(90deg, rgba(148,163,184,0.15) 1px, transparent 1px);
    background-size: 28px 28px;
  }}
  #tooltip {{
    position:fixed; pointer-events:none;
    background:#0f172a; color:#f1f5f9;
    font-family:'IBM Plex Sans',sans-serif;
    font-size:12px; font-weight:500;
    padding:6px 12px; border-radius:6px;
    opacity:0; transition:opacity 0.15s;
    max-width:220px; z-index:1000;
    white-space:nowrap;
  }}
  #controls {{
    position:absolute; bottom:14px; right:14px;
    display:flex; gap:8px;
  }}
  .ctrl-btn {{
    background:white; border:1px solid #e2e8f0;
    border-radius:6px; padding:6px 12px;
    font-family:'IBM Plex Sans',sans-serif;
    font-size:11px; font-weight:600;
    color:#475569; cursor:pointer;
    transition:all 0.15s;
  }}
  .ctrl-btn:hover {{ background:#f1f5f9; border-color:#cbd5e1; }}
  #zoom-info {{
    position:absolute; bottom:14px; left:14px;
    font-family:'IBM Plex Mono',monospace;
    font-size:10px; color:#94a3b8;
    background:white; border:1px solid #e2e8f0;
    padding:4px 10px; border-radius:4px;
  }}
</style>
</head>
<body>
<div id="net"></div>
<div id="tooltip"></div>
<div id="controls">
  <button class="ctrl-btn" onclick="fitAll()">⊞ Fit</button>
  <button class="ctrl-btn" onclick="network.moveTo({{scale:1.0}})">1:1</button>
  <button class="ctrl-btn" onclick="network.moveTo({{scale:network.getScale()*1.3}})">+</button>
  <button class="ctrl-btn" onclick="network.moveTo({{scale:network.getScale()*0.75}})">−</button>
</div>
<div id="zoom-info">Scroll para zoom · Arrastar para navegar</div>
<script>
var nodes = new vis.DataSet({nodes_json});
var edges = new vis.DataSet({edges_json});
var container = document.getElementById('net');
var tooltip = document.getElementById('tooltip');

var options = {{
  physics: {{ enabled: false }},
  interaction: {{
    dragNodes: false,
    zoomView: true,
    dragView: true,
    hover: true,
    tooltipDelay: 0,
    hideEdgesOnDrag: true,
    keyboard: {{ enabled: true }},
  }},
  nodes: {{
    imagePadding: 0,
    shapeProperties: {{ useBorderWithImage: false, interpolation: false }},
    borderWidth: 0,
    size: 125,
  }},
  edges: {{
    hoverWidth: 0.5,
    selectionWidth: 0,
  }},
}};

var network = new vis.Network(container, {{nodes, edges}}, options);

network.on('hoverNode', function(e) {{
  var node = nodes.get(e.node);
  if (node) {{
    tooltip.textContent = node.title;
    tooltip.style.opacity = '1';
  }}
}});
network.on('blurNode', function() {{
  tooltip.style.opacity = '0';
}});
document.addEventListener('mousemove', function(e) {{
  tooltip.style.left = (e.clientX + 14) + 'px';
  tooltip.style.top  = (e.clientY - 30) + 'px';
}});

network.on('zoom', function(e) {{
  document.getElementById('zoom-info').textContent =
    'Zoom: ' + Math.round(e.scale * 100) + '% · Scroll para zoom · Arrastar para navegar';
}});

function fitAll() {{
  network.fit({{animation: {{duration: 500, easingFunction: 'easeInOutQuad'}}}});
}}
fitAll();
</script>
</body></html>"""


# ──────────────────────────────────────────────────────────────────────────────
# COMPONENTES DE UI
# ──────────────────────────────────────────────────────────────────────────────
def metric_card(value, label, sub="", accent="#2563eb"):
    return f"""
    <div class="metric-card" style="--accent:{accent}">
        <div class="metric-val">{value}</div>
        <div class="metric-lbl">{label}</div>
        {"<div class='metric-sub'>" + sub + "</div>" if sub else ""}
    </div>"""


def section_divider(label: str):
    st.markdown(f"""
    <div class="section-divider">
        <div class="section-divider-label">{label}</div>
        <div class="section-divider-line"></div>
    </div>""", unsafe_allow_html=True)


def node_detail_panel(node: dict, upstream: set, downstream: set, nodes_map: dict):
    palette = PALETTE[node["color_key"]]
    
    st.markdown(f"""
    <div class="node-detail">
        <div class="node-detail-header">Nó Selecionado</div>
        <div class="node-detail-title" style="--accent-color:{palette['main']}">
            {node['label']}
        </div>
        <span class="node-badge" style="background:{palette['bg']};color:{palette['text']};border:1px solid {palette['border']}">
            {palette['icon']} {palette['name']}
        </span>
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            metric_card(len(upstream), "Origens", "processos upstream", "#7c3aed"),
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            metric_card(len(downstream), "Impactos", "processos downstream", "#15803d"),
            unsafe_allow_html=True
        )

    if upstream:
        section_divider("DEPENDE DE")
        for uid in list(upstream)[:8]:
            n = nodes_map.get(uid, {})
            if n:
                p = PALETTE[n["color_key"]]
                st.markdown(f"""
                <div class="dependency-item">
                    <span style="color:{p['main']};font-size:14px">{p['icon']}</span>
                    <span>{n['label']}</span>
                </div>""", unsafe_allow_html=True)
        if len(upstream) > 8:
            st.caption(f"+ {len(upstream)-8} outros processos upstream")

    if downstream:
        section_divider("DESBLOQUEIA")
        for did in list(downstream)[:8]:
            n = nodes_map.get(did, {})
            if n:
                p = PALETTE[n["color_key"]]
                st.markdown(f"""
                <div class="dependency-item">
                    <span style="color:{p['main']};font-size:14px">{p['icon']}</span>
                    <span>{n['label']}</span>
                </div>""", unsafe_allow_html=True)
        if len(downstream) > 8:
            st.caption(f"+ {len(downstream)-8} outros processos impactados")


# ──────────────────────────────────────────────────────────────────────────────
# TABS DE CONTEÚDO
# ──────────────────────────────────────────────────────────────────────────────
def tab_mapa(nodes_map, edges, adj, active_id, filter_mode_key):
    html = build_graph_html(
        nodes_map, edges, adj,
        active_id=active_id,
        filter_mode=filter_mode_key,
        height=640,
    )
    st.markdown('<div class="canvas-wrapper">', unsafe_allow_html=True)
    components.html(html, height=644, scrolling=False)
    st.markdown('</div>', unsafe_allow_html=True)


def tab_pipeline(nodes_map, adj, metrics):
    section_divider("COMPOSIÇÃO POR MACROETAPA")
    
    for ck in PIPELINE_ORDER:
        nodes_in_stage = metrics["by_stage"].get(ck, [])
        if not nodes_in_stage:
            continue
        palette = PALETTE[ck]
        avg_degree = (
            sum(len(adj[n]["in"]) + len(adj[n]["out"]) for n in nodes_in_stage) / len(nodes_in_stage)
            if nodes_in_stage else 0
        )
        st.markdown(f"""
        <div class="pipeline-row" style="border-left:3px solid {palette['main']}">
            <span class="pipeline-icon" style="color:{palette['main']}">{palette['icon']}</span>
            <span class="pipeline-name">{palette['name']}</span>
            <span class="pipeline-count">{len(nodes_in_stage)} nós</span>
            <span class="pipeline-count" style="color:#64748b">Grau médio: {avg_degree:.1f}</span>
        </div>""", unsafe_allow_html=True)
        
        with st.expander(f"Ver {len(nodes_in_stage)} processos →", expanded=False):
            cols = st.columns(2)
            for i, nid in enumerate(nodes_in_stage):
                nd = nodes_map[nid]
                deg = len(adj[nid]["in"]) + len(adj[nid]["out"])
                with cols[i % 2]:
                    st.markdown(f"""
                    <div style="padding:6px 10px; background:{palette['bg']};
                         border:1px solid {palette['border']}; border-radius:6px;
                         margin-bottom:4px; font-size:12px; color:{palette['text']}">
                        <strong>{nd['label']}</strong>
                        <span style="float:right; color:#94a3b8; font-size:10px">
                            ↑{len(adj[nid]['in'])} ↓{len(adj[nid]['out'])}
                        </span>
                    </div>""", unsafe_allow_html=True)

    section_divider("TOP 5 NÓS CRÍTICOS")
    for rank, (nid, degree) in enumerate(metrics["top5"], 1):
        nd = nodes_map[nid]
        palette = PALETTE[nd["color_key"]]
        bar_w = int((degree / (metrics["top5"][0][1] + 1)) * 100)
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:12px; padding:8px 0;
             border-bottom:1px solid #f1f5f9;">
            <span style="font-family:'IBM Plex Mono',monospace; font-size:11px;
                  color:#94a3b8; width:20px">#{rank}</span>
            <span style="font-size:13px; font-weight:600; color:{palette['text']}; flex:1">
                {nd['label']}
            </span>
            <div style="width:80px; background:#f1f5f9; height:4px; border-radius:2px; overflow:hidden;">
                <div style="width:{bar_w}%; height:100%; background:{palette['main']}; border-radius:2px;"></div>
            </div>
            <span style="font-family:'IBM Plex Mono',monospace; font-size:11px; color:#64748b; width:30px; text-align:right">
                {degree}
            </span>
        </div>""", unsafe_allow_html=True)


def tab_busca(nodes_map, adj):
    query = st.text_input(
        "🔍",
        placeholder="Buscar processo, relatório, gatilho...",
        label_visibility="collapsed"
    )
    
    if query and len(query) >= 2:
        q = query.lower()
        results = [
            nd for nd in nodes_map.values()
            if q in nd["label"].lower() or q in nd["full_text"].lower()
        ]
        
        if results:
            st.markdown(f"<div style='font-size:11px; color:#94a3b8; margin-bottom:10px'>{len(results)} resultado(s) para «{query}»</div>", unsafe_allow_html=True)
            for nd in results[:20]:
                palette = PALETTE[nd["color_key"]]
                degree_in = len(adj[nd["id"]]["in"])
                degree_out = len(adj[nd["id"]]["out"])
                st.markdown(f"""
                <div class="search-result" style="border-color:{palette['border']}; background:{palette['bg']}">
                    <div class="search-result-type" style="color:{palette['main']}">{palette['icon']} {palette['name']}</div>
                    <div class="search-result-name" style="color:{palette['text']}">{nd['label']}</div>
                    <div style="font-size:10px; color:#94a3b8; margin-top:4px">
                        ↑ {degree_in} entradas  ·  ↓ {degree_out} saídas
                    </div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='padding:20px; text-align:center; color:#94a3b8; font-size:13px'>Nenhum resultado para «{query}»</div>", unsafe_allow_html=True)
    else:
        section_divider("GATILHOS DO FECHAMENTO")
        for gid in [nd for nid, nd in nodes_map.items() if nd["color_key"] == "6"]:
            palette = PALETTE["6"]
            d_out = len(adj[gid["id"]]["out"])
            st.markdown(f"""
            <div class="pipeline-row" style="border-left:3px solid {palette['main']}">
                <span style="color:{palette['main']};font-size:14px">{palette['icon']}</span>
                <span class="pipeline-name" style="color:{palette['text']}">{gid['label']}</span>
                <span class="pipeline-count" style="color:{palette['main']}">→ {d_out} desbloqueios</span>
            </div>""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────────────────
def render_sidebar(nodes_map, adj, metrics):
    with st.sidebar:
        st.markdown("""
        <div style="padding:12px 0 20px">
            <div style="font-family:'IBM Plex Mono',monospace; font-size:10px;
                 letter-spacing:2px; color:#475569; text-transform:uppercase; margin-bottom:4px">
                Controladoria
            </div>
            <div style="font-size:18px; font-weight:700; color:#f1f5f9; line-height:1.2">
                Inteligência<br>Operacional
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Métricas compactas no sidebar
        n = metrics["n_total"]
        e = metrics["n_edges"]
        g = len(metrics["gatilhos"])
        st.markdown(f"""
        <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px; margin-bottom:20px">
            <div style="background:#1e293b; border:1px solid #334155; border-radius:6px; padding:10px; text-align:center">
                <div style="font-family:'IBM Plex Mono',monospace; font-size:18px; font-weight:600; color:#f1f5f9">{n}</div>
                <div style="font-size:9px; letter-spacing:1px; text-transform:uppercase; color:#475569; margin-top:2px">Nós</div>
            </div>
            <div style="background:#1e293b; border:1px solid #334155; border-radius:6px; padding:10px; text-align:center">
                <div style="font-family:'IBM Plex Mono',monospace; font-size:18px; font-weight:600; color:#f1f5f9">{e}</div>
                <div style="font-size:9px; letter-spacing:1px; text-transform:uppercase; color:#475569; margin-top:2px">Links</div>
            </div>
            <div style="background:#1e293b; border:1px solid #334155; border-radius:6px; padding:10px; text-align:center">
                <div style="font-family:'IBM Plex Mono',monospace; font-size:18px; font-weight:600; color:#7c3aed">{g}</div>
                <div style="font-size:9px; letter-spacing:1px; text-transform:uppercase; color:#475569; margin-top:2px">Gatilhos</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="height:1px; background:#1e293b; margin-bottom:16px"></div>', unsafe_allow_html=True)

        # Seleção de processo
        options = {"": None}
        options.update({nd["label"]: nid for nid, nd in sorted(nodes_map.items(), key=lambda x: x[1]["label"])})
        
        selected_label = st.selectbox(
            "Processo Focal",
            list(options.keys()),
            help="Selecione um processo para analisar suas dependências"
        )
        active_id = options.get(selected_label)

        # Modo de filtro
        filter_labels = {
            "⇄ Cadeia completa": "both",
            "← Upstream (origens)": "up",
            "→ Downstream (impactos)": "down",
        }
        filter_label = st.radio(
            "Linhagem",
            list(filter_labels.keys()),
        )
        filter_mode = filter_labels[filter_label]

        # Detalhe do nó selecionado
        if active_id:
            st.markdown('<div style="height:1px; background:#1e293b; margin:16px 0"></div>', unsafe_allow_html=True)
            node = nodes_map[active_id]
            upstream, downstream = get_lineage(active_id, adj)
            node_detail_panel(node, upstream, downstream, nodes_map)

        return active_id, filter_mode


# ──────────────────────────────────────────────────────────────────────────────
# HEADER PRINCIPAL
# ──────────────────────────────────────────────────────────────────────────────
def render_header(metrics, nodes_map, active_id):
    st.markdown("""
    <div style="display:flex; align-items:baseline; gap:12px; margin-bottom:4px">
        <span style="font-family:'IBM Plex Mono',monospace; font-size:11px;
              letter-spacing:2px; text-transform:uppercase; color:#94a3b8">
            Codeme Engenharia
        </span>
        <span style="font-size:11px; color:#e2e8f0; background:#334155;
              padding:2px 8px; border-radius:4px; font-size:10px; font-weight:600; letter-spacing:0.5px">
            Fechamento Gerencial
        </span>
    </div>
    <h1 style="font-size:26px; font-weight:700; color:#0f172a; margin:0 0 16px;
          letter-spacing:-0.5px; font-family:'IBM Plex Sans',sans-serif">
        Arquitetura Operacional de Controladoria
    </h1>
    """, unsafe_allow_html=True)

    # Barra de métricas horizontais
    cols = st.columns(6)
    stage_counts = metrics["by_stage"]
    
    for i, ck in enumerate(PIPELINE_ORDER):
        palette = PALETTE[ck]
        count = len(stage_counts.get(ck, []))
        with cols[i]:
            st.markdown(
                metric_card(count, palette["name"].split("&")[0].strip(),
                            accent=palette["main"]),
                unsafe_allow_html=True
            )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────
def main():
    inject_global_css()

    nodes_map, edges, adj = load_canvas()

    if not nodes_map:
        st.error("⚠️ Arquivo FLUXO_FINAL.canvas não encontrado. Coloque-o na mesma pasta do app.py.")
        st.stop()

    metrics = compute_metrics(nodes_map, edges, adj)

    # Sidebar retorna seleções
    active_id, filter_mode = render_sidebar(nodes_map, adj, metrics)

    # Header
    render_header(metrics, nodes_map, active_id)

    # Legenda de macroetapas
    legend_items = "".join([
        f"<span style='display:inline-flex; align-items:center; gap:5px; margin:3px 6px 3px 0; "
        f"padding:4px 12px; border-radius:20px; font-size:11px; font-weight:600; "
        f"background:{v['bg']}; border:1px solid {v['border']}; color:{v['text']}'>"
        f"<span style='color:{v['main']}'>{v['icon']}</span> {v['name']}</span>"
        for v in PALETTE.values()
    ])
    st.markdown(f"<div style='margin-bottom:16px; line-height:2'>{legend_items}</div>", unsafe_allow_html=True)

    # Tabs principais
    tab1, tab2, tab3 = st.tabs([
        "⬡  Mapa Operacional",
        "⬡  Pipeline & Criticidade",
        "⬡  Busca & Navegação",
    ])

    with tab1:
        tab_mapa(nodes_map, edges, adj, active_id, filter_mode)
        st.caption("Scroll para zoom · Arrastar para navegar · Selecione um processo na barra lateral para isolar a cadeia de dependências")

    with tab2:
        tab_pipeline(nodes_map, adj, metrics)

    with tab3:
        tab_busca(nodes_map, adj)


if __name__ == "__main__":
    main()
