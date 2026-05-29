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
# 1. PALETA FIEL AO OBSIDIAN CANVAS — TEMA CLARO
# ─────────────────────────────────────────────────────────────
OBS_COLORS = {
    "1": {"name": "CONCILIAÇÃO E RESULTADO", "node_bg": "#ffffff", "node_border": "#8b8b8b", "node_text": "#1a1a1a", "edge": "#8b8b8b"},
    "2": {"name": "ANÁLISE FINAL",           "node_bg": "#fffdf5", "node_border": "#e6a817", "node_text": "#4a3200", "edge": "#d4920f"},
    "3": {"name": "APURAÇÃO DE POCs",        "node_bg": "#f5fdf6", "node_border": "#2ea043", "node_text": "#0d3319", "edge": "#2ea043"},
    "4": {"name": "CONFERÊNCIAS NOMINAIS",   "node_bg": "#fff5f5", "node_border": "#e05252", "node_text": "#3d0f0f", "edge": "#d44545"},
    "5": {"name": "BASES DE ORÇAMENTO",      "node_bg": "#f4f8ff", "node_border": "#3b7dd8", "node_text": "#0c2252", "edge": "#3b7dd8"},
    "6": {"name": "GATILHOS",                "node_bg": "#faf5ff", "node_border": "#8b5cf6", "node_text": "#2d1266", "edge": "#8b5cf6"},
}

SKIP_GROUP_IDS = {"4392351365515c6d", "6283cfcedbf60137"}

def clean_label(raw: str) -> str:
    text = raw.replace("[[", "").replace("]]", "")
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if not lines: return raw
    first = lines[0]
    if "/" in first and len(first) > 40:
        first = first.split("/")[-1]
    return first + ("..." if len(lines) > 1 else "")

# ─────────────────────────────────────────────────────────────
# 2. CARREGAMENTO E MAPEAMENTO DE DADOS
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
    
    # Processar nós válidos (ignora grupos na renderização direta para focar na árvore de processos)
    for n in raw_nodes:
        if n.get("type") == "text" and n["id"] not in SKIP_GROUP_IDS:
            color_key = n.get("color", "1")
            c = OBS_COLORS.get(color_key, OBS_COLORS["1"])
            label = clean_label(n.get("text", ""))
            
            nodes_map[n["id"]] = {
                "id": n["id"],
                "label": label,
                "full_text": n.get("text", "").replace("[[", "").replace("]]", ""),
                "color_key": color_key
            }
            
            vis_nodes.append({
                "id": n["id"],
                "label": label,
                "shape": "box",
                "x": n["x"],
                "y": n["y"],
                "color": {"background": c["node_bg"], "border": c["node_border"], "highlight": {"background": "#ffffff", "border": "#0066cc"}},
                "font": {"color": c["node_text"], "size": 12, "face": "Segoe UI, sans-serif"},
                "borderWidth": 1.5,
                "margin": 10
            })
            
    for e in raw_edges:
        if e["fromNode"] in nodes_map and e["toNode"] in nodes_map:
            color_key = e.get("color", "1")
            c = OBS_COLORS.get(color_key, OBS_COLORS["1"])
            vis_edges.append({
                "id": e["id"],
                "from": e["fromNode"],
                "to": e["toNode"],
                "arrows": "to",
                "color": {"color": c["edge"], "opacity": 0.45, "highlight": "#16a34a"},
                "smooth": {"type": "cubicBezier", "roundness": 0.6}
            })
            
    return vis_nodes, vis_edges, nodes_map

vis_nodes, vis_edges, nodes_map = load_canvas_data()

# Rastreamento Recursivo de Linhagem (Upstream/Downstream)
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
# 3. INTERFACE E SIDEBAR (PAINEL DE DETALHES)
# ─────────────────────────────────────────────────────────────

# Injetar estilo CSS para fixar a identidade corporativa clara
st.markdown("""
    <style>
        .block-container { padding-top: 1.5rem; background-color: #f6f8fb; }
        .stSelectbox label { font-size: 11px !important; font-weight: 700; color: #9ca3af; text-transform: uppercase; }
        div[data-testid="stSidebarUserContent"] { background-color: #ffffff; }
    </style>
""", unsafe_allow_html=True)

# Título da Barra Superior
st.markdown("### Fluxo de Fechamento <span style='font-size:16px; color:#6b7280; font-weight:normal;'>— Controladoria</span>", unsafe_allow_html=True)

# Renderizar Legenda em Linha
legenda_html = "".join([
    f"<span style='display:inline-block; margin-right:10px; padding:3px 10px; border-radius:15px; font-size:11px; font-weight:600; background:{OBS_COLORS[k]['node_bg']}; border:1px solid {OBS_COLORS[k]['node_border']}; color:{OBS_COLORS[k]['node_text']};'>● {v['name']}</span>"
    for k, v in OBS_COLORS.items()
])
st.markdown(f"<div style='margin-bottom:15px;'>{legenda_html}</div>", unsafe_allow_html=True)

# Configuração do Sidebar Dinâmico
with st.sidebar:
    st.markdown("### ⇄ Painel de Controle")
    
    search_options = {v["label"]: k for k, v in nodes_map.items()}
    selected_label = st.selectbox("Buscar processo:", [""] + list(search_options.keys()))
    active_id = search_options.get(selected_label, None)
    
    filter_mode = st.radio(
        "Modo de linhagem:",
        ["⟷ Cadeia completa", "← Apenas origens (upstream)", "→ Apenas impactos (downstream)"],
        index=0
    )
    
    st.markdown("---")
    
    if active_id:
        node_info = nodes_map[active_id]
        c = OBS_COLORS[node_info["color_key"]]
        
        # Bloco de Destaque do Nó Selecionado
        st.markdown(f"""
            <div style="background-color: {c['node_bg']}; border: 2px solid {c['node_border']}; border-radius: 8px; padding: 14px; margin-bottom: 15px;">
                <div style="font-size: 9px; font-weight: 700; color: {c['node_border']}; text-transform: uppercase;">Selecionado</div>
                <div style="font-size: 15px; font-weight: 700; color: {c['node_text']};">{node_info['label']}</div>
                <div style="font-size: 12px; color: #6b7280; margin-top: 5px;">{node_info['full_text']}</div>
            </div>
        """, unsafe_allow_html=True)
        
        up_nodes, down_nodes = get_lineage(active_id, vis_edges)
        
        # Seção Upstream
        if "completa" in filter_mode or "origens" in filter_mode:
            st.markdown(f"**Origens ({len(up_nodes)})**")
            if up_nodes:
                chips = "".join([f"<span style='display:inline-block; margin:2px; padding:3px 8px; border-radius:4px; font-size:11px; background:#e8f0fd; border:1px solid #3b7dd8; color:#1e4a8a;'>{nodes_map[n]['label']}</span>" for n in up_nodes])
                st.markdown(f"<div style='max-height:120px; overflow-y:auto;'>{chips}</div>", unsafe_allow_html=True)
            else:
                st.caption("_Processo inicial — sem dependências._")
                
        # Seção Downstream
        if "completa" in filter_mode or "impactos" in filter_mode:
            st.markdown(f"**Impactos ({len(down_nodes)})**")
            if down_nodes:
                chips = "".join([f"<span style='display:inline-block; margin:2px; padding:3px 8px; border-radius:4px; font-size:11px; background:#edfaf0; border:1px solid #2ea043; color:#1a6128;'>{nodes_map[n]['label']}</span>" for n in down_nodes])
                st.markdown(f"<div style='max-height:120px; overflow-y:auto;'>{chips}</div>", unsafe_allow_html=True)
            else:
                st.caption("_Etapa final — não alimenta outros processos._")
    else:
        st.info("💡 Clique ou busque um processo na lista acima para analisar suas amarrações e dependências críticas.")

# ─────────────────────────────────────────────────────────────
# 4. COMPONENTE VISUAL DO CANVAS (VIS.JS INTERATIVO)
# ─────────────────────────────────────────────────────────────
# Modificar dinamicamente as cores caso haja foco ativo
if active_id:
    up_nodes, down_nodes = get_lineage(active_id, vis_edges)
    for node in vis_nodes:
        nid = node["id"]
        if nid == active_id:
            node["borderWidth"] = 3
        elif ("completa" in filter_mode or "origens" in filter_mode) and nid in up_nodes:
            node["color"] = {"background": "#e8f0fd", "border": "#2563eb"}
        elif ("completa" in filter_mode or "impactos" in filter_mode) and nid in down_nodes:
            node["color"] = {"background": "#edfaf0", "border": "#16a34a"}
        else:
            node["color"]["opacity"] = 0.15

# Construção da aplicação injetada via JavaScript no Vis.js
html_source = f"""
<!DOCTYPE html>
<html>
<head>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style type="text/css">
        #network-canvas {{ width: 100%; height: 75vh; background-color: #f6f8fb; border: 1px solid #e8eaed; border-radius: 8px; }}
    </style>
</head>
<body>
    <div id="network-canvas"></div>
    <script type="text/javascript">
        var container = document.getElementById('network-canvas');
        var data = {{
            nodes: new vis.DataSet({json.dumps(vis_nodes)}),
            edges: new vis.DataSet({json.dumps(vis_edges)})
        }};
        var options = {{
            physics: {{ enabled: false }},
            interaction: {{ dragNodes: true, zoomView: true, dragView: true }},
            nodes: {{ fixed: true }}
        }};
        var network = new vis.Network(container, data, options);
    </script>
</body>
</html>
"""

# Renderiza o Canvas no corpo principal da página
components.html(html_source, height=600)
st.caption("ℹ️ Use o scroll do mouse para Zoom. Clique e arraste o fundo para navegar pelo mapa.")
