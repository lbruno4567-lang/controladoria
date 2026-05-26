"""
OPERATIONAL COMPASS — Visualização de Fluxo
Tema: Obsidian Canvas Light Mode (fiel ao original)

Como executar:
  pip install dash dash-cytoscape
  python fluxo_obsidian_light.py
  Acesse: http://127.0.0.1:8050

Coloque o arquivo FLUXO_FINAL.canvas na mesma pasta.
"""

import os
import json
import dash
from dash import html, dcc, Input, Output, State
import dash_cytoscape as cyto

cyto.load_extra_layouts()

# ─────────────────────────────────────────────────────────────
# 1. PALETA FIEL AO OBSIDIAN CANVAS — TEMA CLARO
#    Cores extraídas do app.css do Obsidian (tema Default Light)
# ─────────────────────────────────────────────────────────────
# Cada cor do canvas mapeia para: fundo do card, borda, fundo do grupo, label do grupo
OBS_COLORS = {
    "1": {  # Cinza — CONCILIAÇÃO E RESULTADO
        "node_bg":    "#ffffff",
        "node_border":"#8b8b8b",
        "node_text":  "#1a1a1a",
        "group_bg":   "rgba(139,139,139,0.07)",
        "group_border":"rgba(139,139,139,0.4)",
        "group_label":"#5a5a5a",
        "edge":       "#8b8b8b",
        "tag_bg":     "#f0f0f0",
        "tag_text":   "#5a5a5a",
    },
    "2": {  # Amarelo/Laranja — ANÁLISE FINAL
        "node_bg":    "#fffdf5",
        "node_border":"#e6a817",
        "node_text":  "#4a3200",
        "group_bg":   "rgba(230,168,23,0.06)",
        "group_border":"rgba(230,168,23,0.35)",
        "group_label":"#b07d00",
        "edge":       "#d4920f",
        "tag_bg":     "#fef9e7",
        "tag_text":   "#9a6e00",
    },
    "3": {  # Verde — POCs / APURAÇÃO
        "node_bg":    "#f5fdf6",
        "node_border":"#2ea043",
        "node_text":  "#0d3319",
        "group_bg":   "rgba(46,160,67,0.06)",
        "group_border":"rgba(46,160,67,0.3)",
        "group_label":"#217a32",
        "edge":       "#2ea043",
        "tag_bg":     "#edfaf0",
        "tag_text":   "#1a6128",
    },
    "4": {  # Vermelho/Rosa — CONFERÊNCIAS NOMINAIS
        "node_bg":    "#fff5f5",
        "node_border":"#e05252",
        "node_text":  "#3d0f0f",
        "group_bg":   "rgba(224,82,82,0.05)",
        "group_border":"rgba(224,82,82,0.3)",
        "group_label":"#b03a3a",
        "edge":       "#d44545",
        "tag_bg":     "#ffeeee",
        "tag_text":   "#9c2b2b",
    },
    "5": {  # Azul — BASES DE ORÇAMENTO
        "node_bg":    "#f4f8ff",
        "node_border":"#3b7dd8",
        "node_text":  "#0c2252",
        "group_bg":   "rgba(59,125,216,0.05)",
        "group_border":"rgba(59,125,216,0.3)",
        "group_label":"#2559a7",
        "edge":       "#3b7dd8",
        "tag_bg":     "#e8f0fd",
        "tag_text":   "#1e4a8a",
    },
    "6": {  # Roxo — GATILHOS
        "node_bg":    "#faf5ff",
        "node_border":"#8b5cf6",
        "node_text":  "#2d1266",
        "group_bg":   "rgba(139,92,246,0.05)",
        "group_border":"rgba(139,92,246,0.28)",
        "group_label":"#6d3ec4",
        "edge":       "#8b5cf6",
        "tag_bg":     "#f3ecff",
        "tag_text":   "#5b33a8",
    },
}

SKIP_GROUP_IDS = {"4392351365515c6d", "6283cfcedbf60137"}


# ─────────────────────────────────────────────────────────────
# 2. CARREGAMENTO E PARSE DO CANVAS
# ─────────────────────────────────────────────────────────────
def clean_label(raw: str) -> str:
    """Remove [[...]] e trunca linhas extras."""
    text = raw.replace("[[", "").replace("]]", "")
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if not lines:
        return raw
    first = lines[0]
    # Remove path prefix (01 - GATILHOS/012 - ...)
    if "/" in first and len(first) > 40:
        first = first.split("/")[-1]
    return first + ("…" if len(lines) > 1 else "")


def load_canvas(filename="FLUXO_FINAL.canvas"):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(script_dir, filename)
    if not os.path.exists(path):
        path = filename
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    groups = [n for n in nodes if n.get("type") == "group"]
    texts  = [n for n in nodes if n.get("type") == "text"]

    elements = []

    # Grupos principais (excluindo sub-grupos menores)
    for g in groups:
        if g["id"] in SKIP_GROUP_IDS:
            continue
        c = OBS_COLORS.get(g.get("color", "1"))
        elements.append({
            "data": {
                "id":           g["id"],
                "label":        g.get("label", "").upper(),
                "group_border": c["group_border"],
                "group_bg":     c["group_bg"],
                "group_label":  c["group_label"],
            },
            "position": {
                "x": g["x"] + g["width"] / 2,
                "y": g["y"] + g["height"] / 2,
            },
            "classes": "obs-group",
        })

    # Nós de texto
    for n in texts:
        nid   = n["id"]
        raw   = n.get("text", "")
        color = n.get("color", "1")
        c     = OBS_COLORS.get(color, OBS_COLORS["1"])

        # Determinar grupo pai por sobreposição geométrica
        parent = None
        nx, ny = n["x"], n["y"]
        nw, nh = n.get("width", 200), n.get("height", 60)
        for g in groups:
            if g["id"] in SKIP_GROUP_IDS:
                continue
            if (g["x"] <= nx and g["y"] <= ny and
                    g["x"] + g["width"]  >= nx + nw and
                    g["y"] + g["height"] >= ny + nh):
                parent = g["id"]
                break

        node_data = {
            "id":          nid,
            "label":       clean_label(raw),
            "full_text":   raw.replace("[[", "").replace("]]", ""),
            "color_key":   color,
            "node_bg":     c["node_bg"],
            "node_border": c["node_border"],
            "node_text":   c["node_text"],
            "tag_bg":      c["tag_bg"],
            "tag_text":    c["tag_text"],
        }
        if parent:
            node_data["parent"] = parent

        elements.append({
            "data":     node_data,
            "position": {"x": nx, "y": ny},
            "classes":  "obs-node",
        })

    # Arestas
    for e in edges:
        color = e.get("color", "1")
        c = OBS_COLORS.get(color, OBS_COLORS["1"])
        elements.append({
            "data": {
                "id":     e["id"],
                "source": e["fromNode"],
                "target": e["toNode"],
                "color":  c["edge"],
            },
            "classes": "obs-edge",
        })

    return elements


elements = load_canvas()


# ─────────────────────────────────────────────────────────────
# 3. STYLESHEET — fiel ao Obsidian Canvas Light
# ─────────────────────────────────────────────────────────────
stylesheet = [
    # ── Grupos ──────────────────────────────────────────────
    {
        "selector": ".obs-group",
        "style": {
            "label":              "data(label)",
            "background-color":   "data(group_bg)",
            "border-color":       "data(group_border)",
            "border-width":       "1.5px",
            "border-style":       "solid",
            "shape":              "round-rectangle",
            "corner-radius":      "12px",
            "color":              "data(group_label)",
            "font-size":          "10px",
            "font-weight":        "700",
            "font-family":        "'DM Sans', 'Segoe UI', sans-serif",
            "letter-spacing":     "0.08em",
            "text-valign":        "top",
            "text-halign":        "center",
            "text-margin-y":      "-14px",
            "padding":            "40px",
            "text-transform":     "uppercase",
        },
    },

    # ── Cards de Processo ────────────────────────────────────
    {
        "selector": ".obs-node",
        "style": {
            "label":              "data(label)",
            "width":              "200px",
            "height":             "56px",
            "shape":              "round-rectangle",
            "corner-radius":      "8px",
            "background-color":   "data(node_bg)",
            "color":              "data(node_text)",
            "border-width":       "1.5px",
            "border-color":       "data(node_border)",
            "font-size":          "11px",
            "font-weight":        "500",
            "font-family":        "'DM Sans', 'Segoe UI', sans-serif",
            "text-valign":        "center",
            "text-halign":        "center",
            "text-wrap":          "wrap",
            "text-max-width":     "180px",
            # sombra sutil igual ao Obsidian
            "shadow-blur":        "6px",
            "shadow-color":       "rgba(0,0,0,0.07)",
            "shadow-offset-x":    "0px",
            "shadow-offset-y":    "2px",
            "shadow-opacity":     "1",
            "transition-property":"background-color, border-color, opacity, border-width",
            "transition-duration":"0.12s",
        },
    },

    # ── Arestas ──────────────────────────────────────────────
    {
        "selector": ".obs-edge",
        "style": {
            "width":               "1.8px",
            "line-color":          "data(color)",
            "target-arrow-shape":  "triangle",
            "target-arrow-color":  "data(color)",
            "arrow-scale":         "0.9",
            "curve-style":         "taxi",
            "taxi-direction":      "horizontal",
            "taxi-turn":           "40px",
            "opacity":             "0.45",
            "transition-property": "opacity, width",
            "transition-duration": "0.12s",
        },
    },

    # ── Estados de foco ──────────────────────────────────────
    {
        "selector": ".state-faded",
        "style": {
            "opacity": "0.1",
        },
    },
    {
        "selector": ".state-faded-edge",
        "style": {
            "opacity": "0.04",
        },
    },
    {
        "selector": ".state-focused",
        "style": {
            "background-color":  "#ffffff",
            "border-color":      "#0066cc",
            "border-width":      "2.5px",
            "color":             "#003d7a",
            "font-weight":       "700",
            "shadow-blur":       "12px",
            "shadow-color":      "rgba(0,102,204,0.18)",
            "shadow-offset-x":   "0px",
            "shadow-offset-y":   "0px",
            "shadow-opacity":    "1",
            "opacity":           "1",
            "z-index":           "10",
        },
    },
    {
        "selector": ".state-upstream",
        "style": {
            "border-color":  "#2563eb",
            "border-width":  "2px",
            "color":         "#1d3f8a",
            "opacity":       "1",
            "font-weight":   "600",
        },
    },
    {
        "selector": ".state-downstream",
        "style": {
            "border-color":  "#16a34a",
            "border-width":  "2px",
            "color":         "#0f4a2a",
            "opacity":       "1",
            "font-weight":   "600",
        },
    },
    {
        "selector": ".edge-upstream",
        "style": {
            "line-color":          "#2563eb",
            "target-arrow-color":  "#2563eb",
            "width":               "2.5px",
            "opacity":             "0.9",
        },
    },
    {
        "selector": ".edge-downstream",
        "style": {
            "line-color":          "#16a34a",
            "target-arrow-color":  "#16a34a",
            "width":               "2.5px",
            "opacity":             "0.9",
        },
    },
]


# ─────────────────────────────────────────────────────────────
# 4. LEGENDA DE CORES (espelha o Obsidian)
# ─────────────────────────────────────────────────────────────
LEGENDA = [
    ("1", "CONCILIAÇÃO E RESULTADO"),
    ("5", "BASES DE ORÇAMENTO"),
    ("4", "CONFERÊNCIAS NOMINAIS"),
    ("3", "APURAÇÃO DE POCs"),
    ("6", "GATILHOS"),
    ("2", "ANÁLISE FINAL"),
]


def legenda_pill(key, label):
    c = OBS_COLORS[key]
    return html.Div(style={
        "display":       "flex",
        "alignItems":    "center",
        "gap":           "7px",
        "padding":       "4px 10px",
        "borderRadius":  "20px",
        "border":        f"1px solid {c['group_border']}",
        "backgroundColor": c["group_bg"],
        "fontSize":      "10px",
        "fontWeight":    "600",
        "color":         c["group_label"],
        "letterSpacing": "0.04em",
        "whiteSpace":    "nowrap",
    }, children=[
        html.Div(style={
            "width":        "7px",
            "height":       "7px",
            "borderRadius": "50%",
            "backgroundColor": c["node_border"],
            "flexShrink":   "0",
        }),
        label,
    ])


# ─────────────────────────────────────────────────────────────
# 5. INTERFACE
# ─────────────────────────────────────────────────────────────
app = dash.Dash(__name__, update_title=None)
server = app.server

# Opções de pesquisa (apenas nós texto, sem grupos/sub-grupos)
search_options = [
    {"label": x["data"]["label"], "value": x["data"]["id"]}
    for x in elements
    if "label" in x["data"]
    and "source" not in x["data"]
    and not x["data"]["id"].startswith("grp_")
    and x["data"]["id"] not in SKIP_GROUP_IDS
]

app.layout = html.Div(style={
    "backgroundColor": "#f6f8fb",         # fundo canvas Obsidian light
    "fontFamily":      "'DM Sans', 'Segoe UI', system-ui, sans-serif",
    "height":          "100vh",
    "display":         "flex",
    "flexDirection":   "column",
    "overflow":        "hidden",
}, children=[

    # ── TOPBAR ────────────────────────────────────────────────
    html.Div(style={
        "height":          "56px",
        "backgroundColor": "#ffffff",
        "display":         "flex",
        "alignItems":      "center",
        "justifyContent":  "space-between",
        "padding":         "0 24px",
        "borderBottom":    "1px solid #e8eaed",
        "boxShadow":       "0 1px 3px rgba(0,0,0,0.04)",
        "gap":             "16px",
        "flexShrink":      "0",
    }, children=[

        # Título + legenda
        html.Div(style={"display": "flex", "alignItems": "center", "gap": "20px", "minWidth": 0}, children=[
            html.Div(style={"flexShrink": 0}, children=[
                html.Span("Fluxo de Fechamento", style={
                    "fontSize":   "13px",
                    "fontWeight": "700",
                    "color":      "#111827",
                    "letterSpacing": "-0.01em",
                }),
                html.Span(" — Controladoria", style={
                    "fontSize": "12px",
                    "color":    "#6b7280",
                }),
            ]),
            # Legenda de cores
            html.Div(style={
                "display":    "flex",
                "gap":        "6px",
                "flexWrap":   "wrap",
                "alignItems": "center",
            }, children=[legenda_pill(k, l) for k, l in LEGENDA]),
        ]),

        # Pesquisa + botão toggle
        html.Div(style={"display": "flex", "alignItems": "center", "gap": "10px", "flexShrink": 0}, children=[
            dcc.Dropdown(
                id="search-node",
                options=search_options,
                placeholder="Buscar processo…",
                style={
                    "width":     "280px",
                    "fontSize":  "12px",
                    "border":    "1px solid #e5e7eb",
                    "borderRadius": "6px",
                },
                clearable=True,
            ),
            html.Button("⇄ Painel", id="toggle-btn", n_clicks=0, style={
                "backgroundColor": "#f3f4f6",
                "color":           "#374151",
                "border":          "1px solid #d1d5db",
                "padding":         "6px 14px",
                "borderRadius":    "6px",
                "fontSize":        "12px",
                "fontWeight":      "500",
                "cursor":          "pointer",
            }),
        ]),
    ]),

    # ── CORPO ─────────────────────────────────────────────────
    html.Div(style={"display": "flex", "flex": "1", "overflow": "hidden"}, children=[

        # Grafo
        html.Div(style={"flex": "1", "position": "relative"}, children=[
            cyto.Cytoscape(
                id="cyto-graph",
                elements=elements,
                style={"width": "100%", "height": "100%", "backgroundColor": "#f6f8fb"},
                stylesheet=stylesheet,
                layout={"name": "preset"},
                zoom=0.38,
                pan={"x": 380, "y": 420},
                minZoom=0.05,
                maxZoom=3.0,
            ),
            # Dica de zoom flutuante
            html.Div("Scroll para zoom · Arrastar para navegar", style={
                "position":        "absolute",
                "bottom":          "16px",
                "left":            "50%",
                "transform":       "translateX(-50%)",
                "fontSize":        "10px",
                "color":           "#9ca3af",
                "backgroundColor": "rgba(255,255,255,0.85)",
                "padding":         "4px 12px",
                "borderRadius":    "20px",
                "border":          "1px solid #e5e7eb",
                "pointerEvents":   "none",
                "backdropFilter":  "blur(4px)",
            }),
        ]),

        # ── PAINEL LATERAL ────────────────────────────────────
        html.Div(id="side-panel", style={
            "width":           "360px",
            "backgroundColor": "#ffffff",
            "borderLeft":      "1px solid #e8eaed",
            "display":         "flex",
            "flexDirection":   "column",
            "overflow":        "hidden",
            "transition":      "width 0.22s ease",
            "flexShrink":      "0",
        }, children=[

            html.Div(style={
                "padding":       "20px 22px",
                "flex":          "1",
                "overflowY":     "auto",
                "display":       "flex",
                "flexDirection": "column",
                "gap":           "16px",
                "width":         "316px",  # 360 - 44px padding
            }, children=[

                # Modo de filtro
                html.Div(children=[
                    html.Label("Modo de linhagem", style={
                        "fontSize":   "10px",
                        "fontWeight": "700",
                        "color":      "#9ca3af",
                        "letterSpacing": "0.08em",
                        "textTransform": "uppercase",
                        "display":    "block",
                        "marginBottom": "6px",
                    }),
                    dcc.Dropdown(
                        id="filter-mode",
                        options=[
                            {"label": "⟷  Cadeia completa",          "value": "all"},
                            {"label": "←  Apenas origens (upstream)", "value": "before"},
                            {"label": "→  Apenas impactos (downstream)", "value": "after"},
                        ],
                        value="all",
                        clearable=False,
                        style={"fontSize": "12px"},
                    ),
                ]),

                html.Hr(style={"border": "none", "borderTop": "1px solid #f0f0f0", "margin": "0"}),

                # Conteúdo dinâmico
                html.Div(id="panel-detail", children=[
                    html.Div(style={
                        "textAlign":     "center",
                        "padding":       "32px 16px",
                        "color":         "#9ca3af",
                        "fontSize":      "12px",
                        "border":        "1.5px dashed #e5e7eb",
                        "borderRadius":  "8px",
                        "lineHeight":    "1.6",
                    }, children=[
                        html.Div("↖", style={"fontSize": "24px", "marginBottom": "8px", "opacity": "0.4"}),
                        "Clique em qualquer card para ver origens e impactos do processo",
                    ]),
                ]),
            ]),
        ]),
    ]),
])


# ─────────────────────────────────────────────────────────────
# 6. CALLBACKS
# ─────────────────────────────────────────────────────────────

@app.callback(
    Output("side-panel", "style"),
    Output("toggle-btn", "style"),
    Input("toggle-btn", "n_clicks"),
    State("side-panel", "style"),
    State("toggle-btn", "style"),
)
def toggle_panel(n, panel_style, btn_style):
    p = dict(panel_style)
    b = dict(btn_style)
    if n % 2 == 1:
        p["width"] = "0px"
        b["backgroundColor"] = "#111827"
        b["color"] = "#ffffff"
        b["borderColor"] = "#111827"
    else:
        p["width"] = "360px"
        b["backgroundColor"] = "#f3f4f6"
        b["color"] = "#374151"
        b["borderColor"] = "#d1d5db"
    return p, b


@app.callback(
    Output("cyto-graph", "elements"),
    Output("panel-detail", "children"),
    Input("cyto-graph", "tapNodeData"),
    Input("search-node", "value"),
    Input("filter-mode", "value"),
)
def update_view(tap_data, search_id, mode):
    import dash
    ctx = dash.callback_context
    trigger = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None

    active_id = None
    if trigger == "cyto-graph" and tap_data:
        active_id = tap_data["id"]
    elif trigger == "search-node" and search_id:
        active_id = search_id
    elif trigger == "filter-mode":
        active_id = search_id or (tap_data["id"] if tap_data else None)

    # Ignorar grupos
    if active_id and (
        active_id.startswith("grp_") or
        active_id in SKIP_GROUP_IDS
    ):
        active_id = None

    # ── Sem seleção: resetar ──────────────────────────────────
    if not active_id:
        reset = []
        for el in elements:
            cfg = dict(el)
            if "source" in cfg["data"]:
                cfg["classes"] = "obs-edge"
            elif cfg["data"]["id"].startswith("grp_") or cfg["data"]["id"] in SKIP_GROUP_IDS:
                cfg["classes"] = "obs-group"
            else:
                cfg["classes"] = "obs-node"
            reset.append(cfg)

        placeholder = html.Div(style={
            "textAlign": "center", "padding": "32px 16px",
            "color": "#9ca3af", "fontSize": "12px",
            "border": "1.5px dashed #e5e7eb", "borderRadius": "8px", "lineHeight": "1.6",
        }, children=[
            html.Div("↖", style={"fontSize": "24px", "marginBottom": "8px", "opacity": "0.4"}),
            "Clique em qualquer card para ver origens e impactos do processo",
        ])
        return reset, placeholder

    # ── Traçar upstream / downstream recursivo ────────────────
    all_edges = [x["data"] for x in elements if "source" in x["data"]]

    upstream_nodes, upstream_edges = set(), set()
    def trace_up(nid):
        for e in all_edges:
            if e["target"] == nid and e["id"] not in upstream_edges:
                upstream_edges.add(e["id"])
                upstream_nodes.add(e["source"])
                trace_up(e["source"])
    trace_up(active_id)

    downstream_nodes, downstream_edges = set(), set()
    def trace_down(nid):
        for e in all_edges:
            if e["source"] == nid and e["id"] not in downstream_edges:
                downstream_edges.add(e["id"])
                downstream_nodes.add(e["target"])
                trace_down(e["target"])
    trace_down(active_id)

    def get_label(nid):
        return next((x["data"].get("label", nid) for x in elements if x["data"]["id"] == nid), nid)

    def get_color_key(nid):
        return next((x["data"].get("color_key", "1") for x in elements if x["data"].get("id") == nid), "1")

    # ── Classificar elementos ─────────────────────────────────
    updated = []
    for el in elements:
        cfg = dict(el)
        nid = cfg["data"].get("id", "")

        if "source" in cfg["data"]:
            eid = cfg["data"]["id"]
            if mode in ("all", "before") and eid in upstream_edges:
                cfg["classes"] = "obs-edge edge-upstream"
            elif mode in ("all", "after") and eid in downstream_edges:
                cfg["classes"] = "obs-edge edge-downstream"
            else:
                cfg["classes"] = "obs-edge state-faded-edge"

        elif nid.startswith("grp_") or nid in SKIP_GROUP_IDS:
            cfg["classes"] = "obs-group"

        else:
            if nid == active_id:
                cfg["classes"] = "obs-node state-focused"
            elif mode in ("all", "before") and nid in upstream_nodes:
                cfg["classes"] = "obs-node state-upstream"
            elif mode in ("all", "after") and nid in downstream_nodes:
                cfg["classes"] = "obs-node state-downstream"
            else:
                cfg["classes"] = "obs-node state-faded"

        updated.append(cfg)

    # ── Painel de detalhe ─────────────────────────────────────
    sel = next(x["data"] for x in elements if x["data"]["id"] == active_id)
    ck  = sel.get("color_key", "1")
    c   = OBS_COLORS[ck]

    def node_chip(nid, variant="neutral"):
        ck2 = get_color_key(nid)
        c2  = OBS_COLORS[ck2]
        return html.Div(get_label(nid), style={
            "fontSize":        "11px",
            "padding":         "4px 10px",
            "borderRadius":    "5px",
            "border":          f"1px solid {c2['node_border']}",
            "backgroundColor": c2["node_bg"],
            "color":           c2["node_text"],
            "fontWeight":      "500",
            "cursor":          "default",
        })

    def section(title, dot_color, items, empty_msg):
        return html.Div(children=[
            html.Div(style={"display": "flex", "alignItems": "center", "gap": "7px", "marginBottom": "8px"}, children=[
                html.Div(style={
                    "width": "7px", "height": "7px",
                    "borderRadius": "50%",
                    "backgroundColor": dot_color,
                    "flexShrink": "0",
                }),
                html.Span(title, style={
                    "fontSize": "10px", "fontWeight": "700",
                    "color": dot_color, "letterSpacing": "0.07em",
                    "textTransform": "uppercase",
                }),
                html.Span(f"({len(items)})", style={"fontSize": "10px", "color": "#9ca3af"}),
            ]),
            html.Div(style={
                "display": "flex", "flexWrap": "wrap", "gap": "5px",
                "maxHeight": "130px", "overflowY": "auto",
                "padding": "8px",
                "backgroundColor": "#fafafa",
                "borderRadius": "7px",
                "border": "1px solid #f0f0f0",
            }, children=(
                [node_chip(n) for n in items]
                if items else
                [html.Span(empty_msg, style={"fontSize": "11px", "color": "#9ca3af", "fontStyle": "italic"})]
            )),
        ])

    show_up   = mode in ("all", "before")
    show_down = mode in ("all", "after")

    panel = html.Div(style={"display": "flex", "flexDirection": "column", "gap": "14px"}, children=[

        # Card do nó selecionado
        html.Div(style={
            "backgroundColor": c["node_bg"],
            "border":          f"2px solid {c['node_border']}",
            "borderRadius":    "8px",
            "padding":         "14px 16px",
        }, children=[
            html.Div("Selecionado", style={
                "fontSize": "9px", "fontWeight": "700",
                "color": c["node_border"], "letterSpacing": "0.1em",
                "textTransform": "uppercase", "marginBottom": "4px",
            }),
            html.Div(sel.get("label", active_id), style={
                "fontSize": "14px", "fontWeight": "700",
                "color": c["node_text"], "lineHeight": "1.3",
            }),
            html.Div(sel.get("full_text", ""), style={
                "fontSize": "11px", "color": "#6b7280",
                "marginTop": "5px", "lineHeight": "1.5",
            }) if sel.get("full_text") and sel["full_text"] != sel.get("label") else None,
        ]),

        section("Origens", "#2563eb", list(upstream_nodes),
                "Processo de origem — sem dependências anteriores.")
        if show_up else None,

        section("Impactos", "#16a34a", list(downstream_nodes),
                "Etapa final — não alimenta processos posteriores.")
        if show_down else None,

    ])

    return updated, panel


if __name__ == "__main__":
    app.run(debug=True, port=8050)
