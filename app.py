"""
Fluxo de Fechamento — Controladoria Codeme
Dashboard de Inteligência Operacional Premium
"""

import os, json, base64
import streamlit as st
import streamlit.components.v1 as components

# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Controladoria — Inteligência Operacional",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"Get Help": None, "Report a bug": None, "About": "Controladoria Codeme"},
)

# ──────────────────────────────────────────────────────────────────────────────
# PALETA
# ──────────────────────────────────────────────────────────────────────────────
PALETTE = {
    "1": {"name": "Conciliação & Resultado", "icon": "◈", "main": "#475569", "bg": "#f8fafc", "border": "#cbd5e1", "text": "#1e293b", "fill": "rgba(71,85,105,0.04)",  "stroke": "rgba(71,85,105,0.25)"},
    "2": {"name": "Análise Final",           "icon": "◆", "main": "#b45309", "bg": "#fffbeb", "border": "#fcd34d", "text": "#78350f", "fill": "rgba(180,83,9,0.05)",   "stroke": "rgba(180,83,9,0.30)"},
    "3": {"name": "Apuração de POCs",        "icon": "◉", "main": "#15803d", "bg": "#f0fdf4", "border": "#86efac", "text": "#14532d", "fill": "rgba(21,128,61,0.04)",  "stroke": "rgba(21,128,61,0.28)"},
    "4": {"name": "Conferências Nominais",   "icon": "◎", "main": "#b91c1c", "bg": "#fef2f2", "border": "#fca5a5", "text": "#7f1d1d", "fill": "rgba(185,28,28,0.04)",  "stroke": "rgba(185,28,28,0.28)"},
    "5": {"name": "Bases de Orçamento",      "icon": "◇", "main": "#1d4ed8", "bg": "#eff6ff", "border": "#93c5fd", "text": "#1e3a8a", "fill": "rgba(29,78,216,0.04)",  "stroke": "rgba(29,78,216,0.28)"},
    "6": {"name": "Gatilhos",                "icon": "⚡", "main": "#6d28d9", "bg": "#f5f3ff", "border": "#c4b5fd", "text": "#4c1d95", "fill": "rgba(109,40,217,0.04)", "stroke": "rgba(109,40,217,0.28)"},
}
SKIP_IDS   = {"4392351365515c6d", "6283cfcedbf60137"}
PIPE_ORDER = ["6", "4", "3", "5", "1", "2"]

# ──────────────────────────────────────────────────────────────────────────────
# CSS
# ──────────────────────────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');
    html,body,[class*="css"]{font-family:'IBM Plex Sans',sans-serif!important;}
    .block-container{padding:1.5rem 2rem 2rem!important;max-width:100%!important;background:#f1f5f9;}
    #MainMenu,footer,header{visibility:hidden;}

    [data-testid="stSidebar"]{background:#0f172a!important;border-right:1px solid #1e293b;}
    [data-testid="stSidebar"] *{color:#e2e8f0!important;}
    [data-testid="stSidebar"] label{font-size:10px!important;font-weight:700!important;
        letter-spacing:1.5px!important;text-transform:uppercase!important;color:#64748b!important;}
    [data-testid="stSidebar"] [data-testid="stSelectbox"]>div>div{
        background:#1e293b!important;border:1px solid #334155!important;
        color:#e2e8f0!important;border-radius:6px!important;}
    [data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p{
        font-size:12px!important;font-weight:500!important;color:#cbd5e1!important;}

    .stTabs [data-baseweb="tab-list"]{background:transparent!important;border-bottom:1px solid #e2e8f0;gap:0;}
    .stTabs [data-baseweb="tab"]{font-family:'IBM Plex Sans',sans-serif!important;font-size:12px!important;
        font-weight:600!important;letter-spacing:.8px!important;text-transform:uppercase!important;
        color:#64748b!important;background:transparent!important;border:none!important;
        border-bottom:3px solid transparent!important;padding:10px 20px!important;}
    .stTabs [aria-selected="true"]{color:#0f172a!important;border-bottom:3px solid #0f172a!important;}
    .stTabs [data-baseweb="tab-panel"]{padding:0!important;}

    .mc{background:white;border:1px solid #e2e8f0;border-radius:8px;padding:14px 16px;
        position:relative;overflow:hidden;}
    .mc::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:var(--acc);}
    .mv{font-family:'IBM Plex Mono',monospace;font-size:26px;font-weight:600;
        color:#0f172a;line-height:1;margin-bottom:4px;}
    .ml{font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#94a3b8;}

    .pr{display:flex;align-items:center;gap:12px;padding:10px 14px;border-radius:6px;
        margin-bottom:4px;background:white;border:1px solid #f1f5f9;}
    .pr:hover{border-color:#e2e8f0;box-shadow:0 1px 4px rgba(0,0,0,.06);}
    .pn{font-size:13px;font-weight:600;color:#1e293b;flex:1;}
    .pc{font-family:'IBM Plex Mono',monospace;font-size:11px;color:#94a3b8;
        background:#f1f5f9;padding:2px 8px;border-radius:4px;}

    .di{font-size:12px;color:#475569;padding:5px 0;border-bottom:1px solid #f1f5f9;
        display:flex;align-items:center;gap:8px;}
    .di:last-child{border-bottom:none;}
    .sd{display:flex;align-items:center;gap:12px;margin:16px 0 10px;}
    .sl{font-size:10px;font-weight:700;letter-spacing:2px;text-transform:uppercase;
        color:#94a3b8;white-space:nowrap;}
    .sline{flex:1;height:1px;background:#e2e8f0;}
    .cw{background:white;border:1px solid #e2e8f0;border-radius:12px;
        overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.05);}
    .sr{background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;
        padding:10px 14px;margin-bottom:6px;}
    ::-webkit-scrollbar{width:5px;height:5px;}
    ::-webkit-scrollbar-track{background:transparent;}
    ::-webkit-scrollbar-thumb{background:#cbd5e1;border-radius:10px;}
    </style>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# UTILITÁRIOS
# ──────────────────────────────────────────────────────────────────────────────
def clean_label(raw: str) -> str:
    t = raw.replace("[[","").replace("]]","").strip()
    lines = [l.strip() for l in t.split("\n") if l.strip()]
    if not lines: return raw
    first = lines[0]
    if "/" in first:
        first = first.split("/")[-1]
    return first[:60]

def svg_b64(svg: str) -> str:
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()

def wrap_words(text: str, max_ch: int = 22) -> list:
    words = text.split()
    lines, cur, cur_len = [], [], 0
    for w in words:
        if cur_len + len(w) + 1 <= max_ch:
            cur.append(w); cur_len += len(w)+1
        else:
            if cur: lines.append(" ".join(cur))
            cur, cur_len = [w], len(w)
    if cur: lines.append(" ".join(cur))
    return lines[:3]

def make_node_svg(label: str, node_w: int, node_h: int, palette: dict, state: str) -> str:
    lines = wrap_words(label, max_ch=max(12, int(node_w / 8)))
    line_h = 15
    total_text_h = len(lines) * line_h
    y0 = (node_h - total_text_h) / 2 + line_h - 2

    text_svg = "".join(
        f'<text x="20" y="{y0+i*line_h:.1f}" '
        f'font-family="IBM Plex Sans,sans-serif" font-size="11" font-weight="600" '
        f'fill="{palette["text"]}">{l}</text>'
        for i, l in enumerate(lines)
    )

    if   state == "focal":      stroke, sw, opacity = "#0f172a", "2.5", "1"
    elif state == "upstream":   stroke, sw, opacity = "#7c3aed", "2",   "1"
    elif state == "downstream": stroke, sw, opacity = "#15803d", "2",   "1"
    elif state == "dimmed":     stroke, sw, opacity = palette["border"], "1", "0.18"
    else:                       stroke, sw, opacity = palette["border"], "1", "1"

    shadow = "" if state == "dimmed" else (
        '<filter id="sh"><feDropShadow dx="0" dy="2" stdDeviation="4" '
        'flood-color="#0f172a" flood-opacity="0.08"/></filter>'
    )
    fattr = '' if state == "dimmed" else 'filter="url(#sh)"'

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{node_w}" height="{node_h}">'
        f'<defs>{shadow}</defs>'
        f'<rect x="1" y="1" width="{node_w-2}" height="{node_h-2}" rx="7" '
        f'fill="{palette["bg"]}" stroke="{stroke}" stroke-width="{sw}" '
        f'{fattr} opacity="{opacity}"/>'
        f'<rect x="1" y="1" width="6" height="{node_h-2}" rx="3" '
        f'fill="{palette["main"]}" opacity="{opacity}"/>'
        f'{text_svg}'
        f'</svg>'
    )
    return svg_b64(svg)


# ──────────────────────────────────────────────────────────────────────────────
# CANVAS
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_canvas(path: str = "FLUXO_FINAL.canvas"):
    if not os.path.exists(path):
        return {}, [], {}, []

    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    nodes_map = {}
    groups    = []

    for n in raw.get("nodes", []):
        if n.get("type") == "group":
            ck = str(n.get("color", "1"))
            p  = PALETTE.get(ck, PALETTE["1"])
            groups.append({
                "id":    n["id"],
                "label": n.get("label", ""),
                "color_key": ck,
                # coordenadas originais (canto superior esquerdo)
                "x": n["x"], "y": n["y"],
                "w": n["width"], "h": n["height"],
                # vis.js usa centro → converter
                "vx": n["x"] + n["width"]  / 2,
                "vy": n["y"] + n["height"] / 2,
                "fill":   p["fill"],
                "stroke": p["stroke"],
                "main":   p["main"],
                "text_color": p["text"],
            })

        elif n.get("type") == "text" and n["id"] not in SKIP_IDS:
            ck = str(n.get("color", "1"))
            w  = int(n.get("width",  250))
            h  = int(n.get("height", 60))
            nodes_map[n["id"]] = {
                "id":   n["id"],
                "label": clean_label(n.get("text", "")),
                "full":  n.get("text", "").replace("[[","").replace("]]","").strip(),
                "color_key": ck,
                "vx": n["x"] + w / 2,
                "vy": n["y"] + h / 2,
                "w": w, "h": h,
            }

    edges = [
        e for e in raw.get("edges", [])
        if e.get("fromNode") in nodes_map and e.get("toNode") in nodes_map
    ]

    adj = {nid: {"in": [], "out": []} for nid in nodes_map}
    for e in edges:
        adj[e["fromNode"]]["out"].append(e["toNode"])
        adj[e["toNode"]]["in"].append(e["fromNode"])

    return nodes_map, edges, adj, groups


@st.cache_data(show_spinner=False)
def compute_metrics(_nodes_map, _edges, _adj):
    by_stage = {k: [] for k in PALETTE}
    for nid, nd in _nodes_map.items():
        by_stage.setdefault(nd["color_key"], []).append(nid)
    crit  = {nid: len(_adj[nid]["in"]) + len(_adj[nid]["out"]) for nid in _nodes_map}
    top5  = sorted(crit.items(), key=lambda x: -x[1])[:5]
    return {
        "n": len(_nodes_map), "e": len(_edges),
        "by_stage": by_stage, "crit": crit, "top5": top5,
        "gatilhos": [nid for nid, nd in _nodes_map.items() if nd["color_key"] == "6"],
    }


def get_lineage(nid: str, adj: dict):
    def bfs(starts, direction):
        visited, q = set(), list(starts)
        while q:
            cur = q.pop(0)
            for nb in adj.get(cur, {}).get(direction, []):
                if nb not in visited:
                    visited.add(nb); q.append(nb)
        return visited
    return bfs(adj[nid]["in"], "in"), bfs(adj[nid]["out"], "out")


# ──────────────────────────────────────────────────────────────────────────────
# GRAFO HTML — grupos renderizados via canvas HTML5 sobreposto
# ──────────────────────────────────────────────────────────────────────────────
def build_graph_html(nodes_map, edges, adj, groups,
                     active_id=None, fmode="both", height=650):

    upstream, downstream = (get_lineage(active_id, adj) if active_id else (set(), set()))

    # ── nós vis.js ──
    vis_nodes = []
    for nid, nd in nodes_map.items():
        palette = PALETTE[nd["color_key"]]
        if active_id:
            if   nid == active_id:                                          state = "focal"
            elif nid in upstream   and fmode in ("both","up"):              state = "upstream"
            elif nid in downstream and fmode in ("both","down"):            state = "downstream"
            else:                                                           state = "dimmed"
        else:
            state = "normal"

        vis_nodes.append({
            "id":    nid,
            "x":     nd["vx"],
            "y":     nd["vy"],
            "shape": "image",
            "image": make_node_svg(nd["label"], nd["w"], nd["h"], palette, state),
            "fixed": {"x": True, "y": True},
            "title": nd["label"],
        })

    # ── arestas vis.js ──
    vis_edges = []
    for e in edges:
        ck = str(e.get("color","1"))
        p  = PALETTE.get(ck, PALETTE["1"])
        fn, tn = e["fromNode"], e["toNode"]
        if active_id:
            is_up   = (tn == active_id) or (fn in upstream   and tn in (upstream   | {active_id}))
            is_down = (fn == active_id) or (fn in (downstream | {active_id}) and tn in downstream)
            hi = (fmode in ("both","up") and is_up) or (fmode in ("both","down") and is_down)
            color, w = ({"color":"#2563eb","opacity":0.9}, 2.5) if hi else ({"color":"#94a3b8","opacity":0.04}, 1)
        else:
            color, w = {"color": p["main"], "opacity": 0.35, "highlight":"#2563eb"}, 1.5
        vis_edges.append({
            "id": e["id"], "from": fn, "to": tn,
            "color": color, "width": w,
            "arrows": {"to": {"enabled": True, "scaleFactor": 0.7}},
            "smooth": {"type": "cubicBezier", "roundness": 0.4},
        })

    # ── dados dos grupos para o canvas HTML5 ──
    groups_json = json.dumps([{
        "label": g["label"],
        "x": g["x"], "y": g["y"], "w": g["w"], "h": g["h"],
        "fill":   g["fill"],
        "stroke": g["stroke"],
        "main":   g["main"],
        "tc":     g["text_color"],
    } for g in groups])

    nj = json.dumps(vis_nodes)
    ej = json.dumps(vis_edges)

    return f"""<!DOCTYPE html><html><head>
<script src="https://unpkg.com/vis-network@9.1.9/standalone/umd/vis-network.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:#f8fafc;overflow:hidden;}}
#wrap{{position:relative;width:100%;height:{height}px;}}
/* grade de pontos no fundo */
#wrap::before{{
  content:'';
  position:absolute;inset:0;
  background-image:
    linear-gradient(rgba(148,163,184,.12) 1px,transparent 1px),
    linear-gradient(90deg,rgba(148,163,184,.12) 1px,transparent 1px);
  background-size:28px 28px;
  pointer-events:none;z-index:0;
}}
/* canvas dos grupos fica ATRÁS do vis canvas */
#grp-canvas{{
  position:absolute;inset:0;
  pointer-events:none;z-index:1;
}}
/* o div do vis.js precisa ter fundo transparente */
#net{{
  position:absolute;inset:0;
  background:transparent!important;
  z-index:2;
}}
#tip{{
  position:fixed;pointer-events:none;
  background:#0f172a;color:#f1f5f9;
  font-family:'IBM Plex Sans',sans-serif;
  font-size:12px;font-weight:500;
  padding:6px 12px;border-radius:6px;
  opacity:0;transition:opacity .15s;
  max-width:280px;z-index:9999;
  white-space:nowrap;
  border:1px solid #334155;
}}
#btns{{position:absolute;bottom:14px;right:14px;display:flex;gap:6px;z-index:10;}}
.btn{{background:white;border:1px solid #e2e8f0;border-radius:6px;
  padding:5px 11px;font-family:'IBM Plex Sans',sans-serif;
  font-size:11px;font-weight:600;color:#475569;cursor:pointer;}}
.btn:hover{{background:#f1f5f9;border-color:#cbd5e1;}}
#zi{{position:absolute;bottom:14px;left:14px;z-index:10;
  font-family:'IBM Plex Mono',monospace;font-size:10px;color:#94a3b8;
  background:white;border:1px solid #e2e8f0;padding:4px 10px;border-radius:4px;}}
</style>
</head><body>
<div id="wrap">
  <canvas id="grp-canvas"></canvas>
  <div id="net"></div>
  <div id="tip"></div>
  <div id="btns">
    <button class="btn" onclick="fitAll()">⊞ Fit</button>
    <button class="btn" onclick="net.moveTo({{scale:1}})">1:1</button>
    <button class="btn" onclick="net.moveTo({{scale:net.getScale()*1.3}})">＋</button>
    <button class="btn" onclick="net.moveTo({{scale:net.getScale()*.75}})">－</button>
  </div>
  <div id="zi">Scroll → zoom · Arrastar → navegar</div>
</div>
<script>
// ── dados ──────────────────────────────────────────────────────────────────
var GROUPS = {groups_json};
var visNodes = new vis.DataSet({nj});
var visEdges = new vis.DataSet({ej});
var tip = document.getElementById('tip');

// ── vis.js ─────────────────────────────────────────────────────────────────
var options = {{
  physics:{{enabled:false}},
  interaction:{{
    dragNodes:false,zoomView:true,dragView:true,
    hover:true,hideEdgesOnDrag:true,
    keyboard:{{enabled:true,bindToWindow:false}},
  }},
  nodes:{{
    shape:"image",
    shapeProperties:{{useImageSize:true,useBorderWithImage:false,interpolation:false}},
    borderWidth:0,shadow:false,
  }},
  edges:{{hoverWidth:.5,selectionWidth:0}},
}};
var net = new vis.Network(
  document.getElementById('net'),
  {{nodes:visNodes,edges:visEdges}},
  options
);

// ── canvas HTML5 para os grupos ────────────────────────────────────────────
var gc  = document.getElementById('grp-canvas');
var ctx = gc.getContext('2d');

function resizeGC(){{
  gc.width  = gc.offsetWidth;
  gc.height = gc.offsetHeight;
}}

function drawGroups(){{
  resizeGC();
  ctx.clearRect(0,0,gc.width,gc.height);
  var scale     = net.getScale();
  var translate = net.getViewPosition();   // {{x,y}} = centro do viewport em coords canvas
  var cx = gc.width  / 2;
  var cy = gc.height / 2;

  // transforma coord canvas-obsidian → pixel tela
  function toScreen(canvasX, canvasY){{
    return {{
      x: cx + (canvasX - translate.x) * scale,
      y: cy + (canvasY - translate.y) * scale,
    }};
  }}

  GROUPS.forEach(function(g){{
    var tl = toScreen(g.x,        g.y);
    var br = toScreen(g.x + g.w,  g.y + g.h);
    var sw = br.x - tl.x;
    var sh = br.y - tl.y;
    var r  = Math.max(4, 10 * scale);   // border-radius escalável

    // fundo preenchido
    ctx.beginPath();
    ctx.roundRect(tl.x, tl.y, sw, sh, r);
    ctx.fillStyle   = g.fill;
    ctx.fill();

    // borda tracejada
    ctx.beginPath();
    ctx.roundRect(tl.x, tl.y, sw, sh, r);
    ctx.setLineDash([6 * scale, 4 * scale]);
    ctx.lineWidth   = Math.max(1, 1.5 * scale);
    ctx.strokeStyle = g.stroke;
    ctx.stroke();
    ctx.setLineDash([]);

    // label no canto superior esquerdo dentro do grupo
    if(g.label){{
      var fontSize = Math.max(9, Math.min(13, 11 * scale));
      ctx.font      = 'bold ' + fontSize + 'px "IBM Plex Sans",sans-serif';
      ctx.fillStyle = g.main;
      ctx.globalAlpha = 0.85;
      var pad = Math.max(6, 10 * scale);
      ctx.fillText(g.label.toUpperCase(), tl.x + pad + 6, tl.y + pad + fontSize);
      ctx.globalAlpha = 1;

      // pequena barra colorida ao lado do label
      ctx.fillStyle   = g.main;
      ctx.globalAlpha = 0.6;
      ctx.fillRect(tl.x + pad, tl.y + pad, 3, fontSize + 2);
      ctx.globalAlpha = 1;
    }}
  }});
}}

// redesenha grupos sempre que o vis move/zoom
net.on('afterDrawing',  drawGroups);
net.on('animationFinished', drawGroups);
window.addEventListener('resize', function(){{ resizeGC(); drawGroups(); }});

// tooltip
net.on('hoverNode', function(e){{
  var n = visNodes.get(e.node);
  if(n){{ tip.textContent=n.title; tip.style.opacity='1'; }}
}});
net.on('blurNode', function(){{ tip.style.opacity='0'; }});
document.addEventListener('mousemove', function(e){{
  tip.style.left=(e.clientX+14)+'px';
  tip.style.top=(e.clientY-34)+'px';
}});

// zoom info
net.on('zoom', function(e){{
  document.getElementById('zi').textContent=
    'Zoom: '+Math.round(e.scale*100)+'% · Scroll → zoom · Arrastar → navegar';
}});

function fitAll(){{
  net.fit({{animation:{{duration:500,easingFunction:'easeInOutQuad'}}}});
}}

net.once('stabilized', function(){{ fitAll(); drawGroups(); }});
fitAll();
</script>
</body></html>"""


# ──────────────────────────────────────────────────────────────────────────────
# HELPERS UI
# ──────────────────────────────────────────────────────────────────────────────
def sdiv(label):
    st.markdown(
        f'<div class="sd"><span class="sl">{label}</span><div class="sline"></div></div>',
        unsafe_allow_html=True)

def mcard(val, label, acc="#475569"):
    return (f'<div class="mc" style="--acc:{acc}">'
            f'<div class="mv">{val}</div><div class="ml">{label}</div></div>')


# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────────────────
def render_sidebar(nodes_map, adj, metrics):
    with st.sidebar:
        st.markdown("""
        <div style="padding:12px 0 18px">
          <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;
               letter-spacing:2px;color:#475569;text-transform:uppercase;margin-bottom:4px">
            Controladoria</div>
          <div style="font-size:18px;font-weight:700;color:#f1f5f9;line-height:1.2">
            Inteligência<br>Operacional</div>
        </div>""", unsafe_allow_html=True)

        n, e, g = metrics["n"], metrics["e"], len(metrics["gatilhos"])
        cells = "".join(f"""
          <div style="background:#1e293b;border:1px solid #334155;border-radius:6px;
               padding:10px;text-align:center">
            <div style="font-family:'IBM Plex Mono',monospace;font-size:18px;font-weight:600;
                 color:{'#7c3aed' if lbl=='Gatilhos' else '#f1f5f9'}">{v}</div>
            <div style="font-size:9px;letter-spacing:1px;text-transform:uppercase;
                 color:#475569;margin-top:2px">{lbl}</div>
          </div>""" for v, lbl in [(n,"Nós"),(e,"Links"),(g,"Gatilhos")])
        st.markdown(f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:18px">'
                    f'{cells}</div>'
                    f'<div style="height:1px;background:#1e293b;margin-bottom:16px"></div>',
                    unsafe_allow_html=True)

        opts = {"": None}
        opts.update({nd["label"]: nid for nid, nd in sorted(nodes_map.items(), key=lambda x: x[1]["label"])})
        sel = st.selectbox("Processo Focal", list(opts.keys()))
        active_id = opts.get(sel)

        fmap = {"⇄ Cadeia completa":"both","← Upstream (origens)":"up","→ Downstream (impactos)":"down"}
        fsel = st.radio("Linhagem", list(fmap.keys()))
        fmode = fmap[fsel]

        if active_id:
            nd = nodes_map[active_id]
            palette = PALETTE[nd["color_key"]]
            up, down = get_lineage(active_id, adj)
            st.markdown('<div style="height:1px;background:#1e293b;margin:14px 0"></div>',
                        unsafe_allow_html=True)
            st.markdown(f"""
            <div style="background:#1e293b;border:1px solid #334155;
                 border-left:3px solid {palette['main']};border-radius:6px;
                 padding:12px;margin-bottom:10px">
              <div style="font-size:9px;letter-spacing:1.5px;text-transform:uppercase;
                   color:{palette['main']};margin-bottom:4px">{palette['icon']} {palette['name']}</div>
              <div style="font-size:14px;font-weight:700;color:#f1f5f9">{nd['label']}</div>
            </div>""", unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1: st.markdown(mcard(len(up),   "Origens",  "#7c3aed"), unsafe_allow_html=True)
            with c2: st.markdown(mcard(len(down),  "Impactos", "#15803d"), unsafe_allow_html=True)

            if up:
                sdiv("DEPENDE DE")
                for uid in list(up)[:7]:
                    n2 = nodes_map.get(uid)
                    if n2:
                        p2 = PALETTE[n2["color_key"]]
                        st.markdown(
                            f'<div class="di"><span style="color:{p2["main"]}">{p2["icon"]}</span>'
                            f'<span style="font-size:11px;color:#cbd5e1">{n2["label"]}</span></div>',
                            unsafe_allow_html=True)
                if len(up) > 7: st.caption(f"+ {len(up)-7} upstream")

            if down:
                sdiv("DESBLOQUEIA")
                for did in list(down)[:7]:
                    n2 = nodes_map.get(did)
                    if n2:
                        p2 = PALETTE[n2["color_key"]]
                        st.markdown(
                            f'<div class="di"><span style="color:{p2["main"]}">{p2["icon"]}</span>'
                            f'<span style="font-size:11px;color:#cbd5e1">{n2["label"]}</span></div>',
                            unsafe_allow_html=True)
                if len(down) > 7: st.caption(f"+ {len(down)-7} downstream")

        return active_id, fmode


# ──────────────────────────────────────────────────────────────────────────────
# TABS
# ──────────────────────────────────────────────────────────────────────────────
def tab_mapa(nodes_map, edges, adj, groups, active_id, fmode):
    html = build_graph_html(nodes_map, edges, adj, groups, active_id, fmode, height=650)
    st.markdown('<div class="cw">', unsafe_allow_html=True)
    components.html(html, height=654, scrolling=False)
    st.markdown('</div>', unsafe_allow_html=True)
    st.caption("Scroll → zoom  ·  Arrastar → navegar  ·  Selecione um processo na barra lateral para isolar dependências")


def tab_pipeline(nodes_map, adj, metrics):
    sdiv("COMPOSIÇÃO POR MACROETAPA")
    for ck in PIPE_ORDER:
        stage_nodes = metrics["by_stage"].get(ck, [])
        if not stage_nodes: continue
        p   = PALETTE[ck]
        avg = sum(len(adj[n]["in"])+len(adj[n]["out"]) for n in stage_nodes)/len(stage_nodes)
        st.markdown(
            f'<div class="pr" style="border-left:3px solid {p["main"]}">'
            f'<span style="color:{p["main"]};font-size:15px">{p["icon"]}</span>'
            f'<span class="pn">{p["name"]}</span>'
            f'<span class="pc">{len(stage_nodes)} nós</span>'
            f'<span class="pc" style="color:#64748b">grau médio {avg:.1f}</span>'
            f'</div>', unsafe_allow_html=True)
        with st.expander(f"Ver {len(stage_nodes)} processos", expanded=False):
            cols = st.columns(2)
            for i, nid in enumerate(stage_nodes):
                nd = nodes_map[nid]
                with cols[i%2]:
                    st.markdown(
                        f'<div style="padding:6px 10px;background:{p["bg"]};'
                        f'border:1px solid {p["border"]};border-radius:6px;margin-bottom:4px;">'
                        f'<span style="font-size:12px;font-weight:600;color:{p["text"]}">{nd["label"]}</span>'
                        f'<span style="float:right;font-size:10px;color:#94a3b8;font-family:monospace">'
                        f'↑{len(adj[nid]["in"])} ↓{len(adj[nid]["out"])}</span></div>',
                        unsafe_allow_html=True)

    sdiv("TOP 5 NÓS CRÍTICOS")
    max_deg = metrics["top5"][0][1] if metrics["top5"] else 1
    for rank, (nid, deg) in enumerate(metrics["top5"], 1):
        nd = nodes_map[nid]; p = PALETTE[nd["color_key"]]
        pct = int(deg/max_deg*100)
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:12px;padding:8px 0;'
            f'border-bottom:1px solid #f1f5f9;">'
            f'<span style="font-family:monospace;font-size:11px;color:#94a3b8;width:20px">#{rank}</span>'
            f'<span style="font-size:13px;font-weight:600;color:{p["text"]};flex:1">{nd["label"]}</span>'
            f'<div style="width:80px;background:#f1f5f9;height:4px;border-radius:2px;overflow:hidden">'
            f'<div style="width:{pct}%;height:100%;background:{p["main"]};border-radius:2px"></div></div>'
            f'<span style="font-family:monospace;font-size:11px;color:#64748b;width:24px;text-align:right">{deg}</span>'
            f'</div>', unsafe_allow_html=True)


def tab_busca(nodes_map, adj):
    query = st.text_input("🔍", placeholder="Buscar processo, relatório, gatilho...",
                          label_visibility="collapsed")
    if query and len(query) >= 2:
        q = query.lower()
        results = [nd for nd in nodes_map.values()
                   if q in nd["label"].lower() or q in nd["full"].lower()]
        st.markdown(f'<div style="font-size:11px;color:#94a3b8;margin-bottom:10px">'
                    f'{len(results)} resultado(s) para «{query}»</div>', unsafe_allow_html=True)
        for nd in results[:25]:
            p  = PALETTE[nd["color_key"]]
            di = len(adj[nd["id"]]["in"]); do = len(adj[nd["id"]]["out"])
            st.markdown(
                f'<div class="sr" style="border-left:3px solid {p["main"]}">'
                f'<div style="font-size:10px;font-weight:700;letter-spacing:.5px;'
                f'text-transform:uppercase;color:{p["main"]}">{p["icon"]} {p["name"]}</div>'
                f'<div style="font-size:13px;font-weight:600;color:{p["text"]};margin:2px 0">{nd["label"]}</div>'
                f'<div style="font-size:10px;color:#94a3b8">↑ {di} entradas  ·  ↓ {do} saídas</div>'
                f'</div>', unsafe_allow_html=True)
    else:
        sdiv("GATILHOS DO FECHAMENTO")
        for nid, nd in nodes_map.items():
            if nd["color_key"] != "6": continue
            p  = PALETTE["6"]
            do = len(adj[nid]["out"])
            st.markdown(
                f'<div class="pr" style="border-left:3px solid {p["main"]}">'
                f'<span style="color:{p["main"]};font-size:15px">{p["icon"]}</span>'
                f'<span class="pn" style="color:{p["text"]}">{nd["label"]}</span>'
                f'<span class="pc" style="color:{p["main"]}">→ {do} desbloqueios</span>'
                f'</div>', unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────────────────────────────────────
def render_header(metrics):
    st.markdown("""
    <div style="display:flex;align-items:baseline;gap:12px;margin-bottom:4px">
      <span style="font-family:'IBM Plex Mono',monospace;font-size:11px;
           letter-spacing:2px;text-transform:uppercase;color:#94a3b8">Codeme Engenharia</span>
      <span style="background:#334155;color:#e2e8f0;padding:2px 8px;border-radius:4px;
           font-size:10px;font-weight:600;letter-spacing:.5px">Fechamento Gerencial</span>
    </div>
    <h1 style="font-size:24px;font-weight:700;color:#0f172a;margin:0 0 16px;
         letter-spacing:-.5px;font-family:'IBM Plex Sans',sans-serif">
      Arquitetura Operacional de Controladoria</h1>""", unsafe_allow_html=True)

    cols = st.columns(6)
    for i, ck in enumerate(PIPE_ORDER):
        p = PALETTE[ck]; count = len(metrics["by_stage"].get(ck,[]))
        with cols[i]:
            st.markdown(mcard(count, p["name"].split("&")[0].strip(), p["main"]),
                        unsafe_allow_html=True)
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    items = "".join(
        f'<span style="display:inline-flex;align-items:center;gap:5px;margin:3px 5px 3px 0;'
        f'padding:4px 12px;border-radius:20px;font-size:11px;font-weight:600;'
        f'background:{v["bg"]};border:1px solid {v["border"]};color:{v["text"]}">'
        f'<span style="color:{v["main"]}">{v["icon"]}</span> {v["name"]}</span>'
        for v in PALETTE.values())
    st.markdown(f'<div style="margin-bottom:14px;line-height:2.2">{items}</div>',
                unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────
def main():
    inject_css()
    nodes_map, edges, adj, groups = load_canvas()

    if not nodes_map:
        st.error("⚠️  FLUXO_FINAL.canvas não encontrado. Coloque-o na mesma pasta do app.py.")
        st.stop()

    metrics = compute_metrics(nodes_map, edges, adj)
    active_id, fmode = render_sidebar(nodes_map, adj, metrics)
    render_header(metrics)

    t1, t2, t3 = st.tabs(["⬡  Mapa Operacional","⬡  Pipeline & Criticidade","⬡  Busca & Navegação"])
    with t1: tab_mapa(nodes_map, edges, adj, groups, active_id, fmode)
    with t2: tab_pipeline(nodes_map, adj, metrics)
    with t3: tab_busca(nodes_map, adj)

if __name__ == "__main__":
    main()
