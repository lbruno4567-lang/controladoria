import os
import json
import dash
from dash import html, dcc, Input, Output
import dash_cytoscape as cyto

# Ativa layouts extras para o Cytoscape, se necessário
cyto.load_extra_layouts()

# -----------------------------------------------------------------------------
# 1. MAPEAMENTO DE CORES (Tema Claro Executivo)
# -----------------------------------------------------------------------------
COLOR_MAP = {
    "1": {"bg": "rgba(168, 168, 168, 0.04)", "stroke": "#64748b"}, # Cinza (Conciliação)
    "2": {"bg": "rgba(224, 155, 67, 0.04)",  "stroke": "#b45309"}, # Laranja (Análise Final)
    "3": {"bg": "rgba(100, 184, 115, 0.04)", "stroke": "#15803d"}, # Verde (POCs)
    "4": {"bg": "rgba(224, 91, 91, 0.04)",   "stroke": "#b91c1c"}, # Vermelho (Análises Nominais)
    "5": {"bg": "rgba(83, 155, 224, 0.04)",  "stroke": "#1d4ed8"}, # Azul (Bases)
    "6": {"bg": "rgba(174, 114, 224, 0.04)", "stroke": "#6d28d9"}, # Roxo (Gatilhos)
}

# -----------------------------------------------------------------------------
# 2. PROCESSAMENTO DO CANVAS COM ANINHAMENTO DE GRUPOS SEGURO
# -----------------------------------------------------------------------------
def load_canvas_with_groups(filename="FLUXO_FINAL.canvas"):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(script_dir, filename)
    
    if not os.path.exists(filepath):
        filepath = filename
        
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    
    group_nodes = [n for n in nodes if n.get("type") == "group"]
    standard_nodes = [n for n in nodes if n.get("type") != "group"]
    
    elements = []
    
    # 1. Adicionar as caixas de Macro-Grupo (Cantos arredondados)
    for g in group_nodes:
        color_cfg = COLOR_MAP.get(g.get("color", "1"), {"bg": "rgba(0,0,0,0.01)", "stroke": "#cbd5e1"})
        label_grupo = g.get("label", "").upper()
        elements.append({
            "data": {
                "id": g["id"],
                "label": label_grupo,
                "stroke_color": color_cfg["stroke"],
                "bg_color": color_cfg["bg"]
            },
            "position": {"x": g["x"] + (g["width"] / 2), "y": g["y"] + (g["height"] / 2)},
            "classes": "group-box"
        })

    # 2. Adicionar os Cards de Processo (Design Arredondado Elegante)
    for n in standard_nodes:
        node_id = n["id"]
        raw_text = n.get("text", n.get("label", node_id))
        
        label = raw_text.replace("[[", "").replace("]]", "").split('\n')[0]
        if len(raw_text.split('\n')) > 1:
            label += "..."
            
        color_cfg = COLOR_MAP.get(n.get("color", "1"), {"bg": "#ffffff", "stroke": "#cbd5e1"})
        
        parent_id = None
        nx, ny = n["x"], n["y"]
        for g in group_nodes:
            if (g["x"] <= nx <= g["x"] + g["width"]) and (g["y"] <= ny <= g["y"] + g["height"]):
                parent_id = g["id"]
                break

        node_data = {
            "id": node_id,
            "label": label,
            "full_text": raw_text,
            "stroke_color": color_cfg["stroke"],
            "bg_color": "#ffffff"
        }
        if parent_id:
            node_data["parent"] = parent_id

        elements.append({
            "data": node_data,
            "position": {"x": nx, "y": ny},
            "classes": "process-node"
        })
        
    # 3. Adicionar as Linhas/Conexões
    for e in edges:
        color_cfg = COLOR_MAP.get(e.get("color", "1"), {"stroke": "#94a3b8"})
        elements.append({
            "data": {
                "id": e["id"],
                "source": e["fromNode"],
                "target": e["toNode"],
                "color": color_cfg["stroke"]
            },
            "classes": "base-edge"
        })
        
    return elements

elements = load_canvas_with_groups()

# -----------------------------------------------------------------------------
# 3. DESIGN SYSTEM PREMIUM (Bordas Arredondadas e Suavidade)
# -----------------------------------------------------------------------------
stylesheet = [
    {
        "selector": ".process-node",
        "style": {
            "label": "data(label)",
            "width": "210px",
            "height": "65px",
            "shape": "round-rectangle",
            "round-corners": "12px",  # Curvatura elegante nos cards
            "background-color": "data(bg_color)",
            "color": "#334155",
            "border-width": "1.5px",
            "border-color": "data(stroke_color)",
            "font-size": "11px",
            "font-weight": "500",
            "text-valign": "center",
            "text-halign": "center",
            "text-wrap": "wrap",
            "text-max-width": "190px",
            "opacity": 1.0,
            "transition-property": "background-color, border-color, opacity, color, width, line-color",
            "transition-duration": "0.15s"
        }
    },
    {
        "selector": ".group-box",
        "style": {
            "label": "data(label)",
            "background-color": "data(bg_color)",
            "border-width": "1px",
            "border-color": "data(stroke_color)",
            "border-style": "solid",
            "shape": "round-rectangle",
            "round-corners": "16px",  # Curvatura elegante nas macro-caixas
            "color": "data(stroke_color)",
            "font-size": "11px",
            "font-weight": "700",
            "text-valign": "top",
            "text-margin-y": "-12px",
            "padding": "45px",
            "opacity": 0.55
        }
    },
    {
        "selector": ".base-edge",
        "style": {
            "width": 2,
            "line-color": "data(color)",
            "target-arrow-shape": "triangle",
            "target-arrow-color": "data(color)",
            "curve-style": "taxi",
            "taxi-direction": "horizontal",
            "opacity": 0.35,
            "transition-property": "opacity, width, line-color",
            "transition-duration": "0.15s"
        }
    },
    
    # Estados de Interação Dinâmica
    {
        "selector": ".faded-node",
        "style": {
            "opacity": 0.15,
            "color": "#94a3b8"
        }
    },
    {
        "selector": ".faded-edge",
        "style": {
            "opacity": 0.02
        }
    },
    {
        "selector": ".node-focused",
        "style": {
            "opacity": 1.0,
            "background-color": "#f0f9ff",
            "color": "#0369a1",
            "border-color": "#0284c7",
            "border-width": "3px",
            "font-weight": "700"
        }
    },
    {
        "selector": ".node-upstream",
        "style": {
            "opacity": 1.0, 
            "border-color": "#2563eb", 
            "border-width": "2.5px", 
            "color": "#1e40af", 
            "background-color": "#ffffff",
            "font-weight": "600"
        }
    },
    {
        "selector": ".edge-upstream",
        "style": {
            "opacity": 1.0, 
            "width": 3.5, 
            "line-color": "#2563eb", 
            "target-arrow-color": "#2563eb"
        }
    },
    {
        "selector": ".node-downstream",
        "style": {
            "opacity": 1.0, 
            "border-color": "#16a34a", 
            "border-width": "2.5px", 
            "color": "#14532d", 
            "background-color": "#ffffff",
            "font-weight": "600"
        }
    },
    {
        "selector": ".edge-downstream",
        "style": {
            "opacity": 1.0, 
            "width": 3.5, 
            "line-color": "#16a34a", 
            "target-arrow-color": "#16a34a"
        }
    }
]

# -----------------------------------------------------------------------------
# 4. MONTAGEM DA INTERFACE (UI DESIGN COM CANTOS SUAVES)
# -----------------------------------------------------------------------------
app = dash.Dash(__name__, update_title=None)

app.layout = html.Div(style={
    "backgroundColor": "#ffffff", "fontFamily": "system-ui, -apple-system, sans-serif",
    "height": "100vh", "display": "flex", "flexDirection": "column", "overflow": "hidden"
}, children=[
    
    # Header Limpo
    html.Div(style={
        "height": "65px", "backgroundColor": "#f8fafc", "display": "flex",
        "alignItems": "center", "justifyContent": "space-between", "padding": "0 30px",
        "borderBottom": "1px solid #e2e8f0"
    }, children=[
        html.Div([
            html.H2("Operational Architecture & Financial Lineage", style={"color": "#0f172a", "margin": 0, "fontSize": "15px", "fontWeight": "600"}),
            html.P("Rastreabilidade e governança de processos de ponta a ponta", style={"color": "#64748b", "margin": "2px 0 0 0", "fontSize": "11px"})
        ]),
        dcc.Dropdown(
            id='search-component',
            options=[{'label': f"[{x['data'].get('label', '')}]", 'value': x['data']['id']} for x in elements if 'label' in x['data'] and 'source' not in x['data'] and not x['data']['id'].startswith('grp_') and x['data']['id'] not in ['4392351365515c6d', '6283cfcedbf60137']],
            placeholder="Pesquisar nó ou indicador específico...",
            style={'width': '340px', 'fontSize': '13px'}
        )
    ]),
    
    # Corpo
    html.Div(style={"display": "flex", "flex": 1}, children=[
        
        # Área do Grafo
        html.Div(style={"flex": 1, "position": "relative", "backgroundColor": "#ffffff"}, children=[
            cyto.Cytoscape(
                id='cytoscape-canvas',
                elements=elements,
                style={'width': '100%', 'height': '100%'},
                stylesheet=stylesheet,
                layout={'name': 'preset'},
                zoom=0.4,
                pan={'x': 100, 'y': 200},
                minZoom=0.05,
                maxZoom=2.5
            )
        ]),
        
        # Painel de Controle e Auditoria Lateral (Bordas internas suavizadas)
        html.Div(id='inspector-panel', style={
            "width": "410px", "backgroundColor": "#f8fafc", "borderLeft": "1px solid #e2e8f0",
            "padding": "25px 30px", "color": "#475569", "display": "flex", "flexDirection": "column",
            "boxShadow": "-2px 0 12px rgba(0,0,0,0.01)"
        }, children=[
            html.H3("Filtros & Linhagem", style={"color": "#0f172a", "marginTop": 0, "fontSize": "14px", "fontWeight": "600", "textTransform": "uppercase", "letterSpacing": "0.5px"}),
            
            # SELETOR DE FILTRO DE CADEIA (Nova Opção Elegante)
            html.Div(style={"marginBottom": "20px", "marginTop": "5px"}, children=[
                html.Label("Modo de Filtro Visual:", style={"fontSize": "11px", "fontWeight": "600", "color": "#64748b", "display": "block", "marginBottom": "6px"}),
                dcc.Dropdown(
                    id='filter-mode',
                    options=[
                        {'label': '🔗 Cadeira Completa (End-to-End)', 'value': 'all'},
                        {'label': '⬅️ Apenas o que vem ANTES (Origens/Upstream)', 'value': 'before'},
                        {'label': '➡️ Apenas o que vem DEPOIS (Impactos/Downstream)', 'value': 'after'}
                    ],
                    value='all',
                    clearable=False,
                    style={'fontSize': '12px', 'borderRadius': '8px'}
                )
            ]),
            
            html.Hr(style={"borderColor": "#e2e8f0", "margin": "10px 0 20px 0"}),
            
            # Conteúdo Dinâmico
            html.Div(id='inspector-content', style={"flex": 1, "overflowY": "auto"}, children=[
                html.Div(style={
                    "border": "1px dashed #cbd5e1", "padding": "20px", "borderRadius": "8px",
                    "textAlign": "center", "fontSize": "12px", "color": "#64748b"
                }, children="Selecione um card para habilitar os filtros de isolamento e auditar o fluxo.")
            ])
        ])
    ])
])

# -----------------------------------------------------------------------------
# 5. LÓGICA DE FILTRAGEM INTELIGENTE RECURSIVA
# -----------------------------------------------------------------------------
@app.callback(
    [Output('cytoscape-canvas', 'elements'), Output('inspector-content', 'children')],
    [Input('cytoscape-canvas', 'tapNodeData'), Input('search-component', 'value'), Input('filter-mode', 'value')]
)
def update_architecture_view(tap_data, searched_id, filter_mode):
    ctx = dash.callback_context
    trigger = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
    active_id = None
    if trigger == 'cytoscape-canvas' and tap_data:
        active_id = tap_data['id']
    elif trigger == 'search-component' and searched_id:
        active_id = searched_id
    elif trigger == 'filter-mode' and (tap_data or searched_id):
        # Se mudou o filtro mas já tinha algo selecionado, mantém o foco ativo
        active_id = searched_id if searched_id else tap_data['id']
        
    if active_id and (active_id.startswith('grp_') or active_id in ['4392351365515c6d', '6283cfcedbf60137']):
        active_id = None

    if not active_id:
        cleaned_elements = []
        for el in elements:
            cfg = el.copy()
            nid = cfg["data"].get("id", "")
            if "source" in cfg["data"]:
                cfg["classes"] = "base-edge"
            elif nid.startswith("grp_") or nid in ['4392351365515c6d', '6283cfcedbf60137']:
                cfg["classes"] = "group-box"
            else:
                cfg["classes"] = "process-node"
            cleaned_elements.append(cfg)
        
        msg = html.Div(style={"border": "1px dashed #cbd5e1", "padding": "20px", "borderRadius": "8px", "textAlign": "center", "fontSize": "12px", "color": "#64748b"}, children="Selecione um card para habilitar os filtros de isolamento e auditar o fluxo.")
        return cleaned_elements, msg

    all_edges = [x['data'] for x in elements if 'source' in x['data']]

    # 1. Mapeamento Recursivo para Trás (Antes / Upstream)
    visited_upstream_nodes = set()
    visited_upstream_edges = set()
    def trace_upstream(node_id):
        for edge in all_edges:
            if edge['target'] == node_id:
                if edge['id'] not in visited_upstream_edges:
                    visited_upstream_edges.add(edge['id'])
                    if edge['source'] not in visited_upstream_nodes:
                        visited_upstream_nodes.add(edge['source'])
                        trace_upstream(edge['source'])
    trace_upstream(active_id)

    # 2. Mapeamento Recursivo para Frente (Depois / Downstream)
    visited_downstream_nodes = set()
    visited_downstream_edges = set()
    def trace_downstream(node_id):
        for edge in all_edges:
            if edge['source'] == node_id:
                if edge['id'] not in visited_downstream_edges:
                    visited_downstream_edges.add(edge['id'])
                    if edge['target'] not in visited_downstream_nodes:
                        visited_downstream_nodes.add(edge['target'])
                        trace_downstream(edge['target'])
    trace_downstream(active_id)

    # 3. Construção dos Elementos Finais Baseados no Tipo de Filtro Escolhido
    updated_elements = []
    for el in elements:
        cfg = el.copy()
        node_id = cfg["data"].get("id")
        
        if "source" in cfg["data"]:
            if filter_mode in ['all', 'before'] and node_id in visited_upstream_edges:
                cfg["classes"] = "base-edge edge-upstream"
            elif filter_mode in ['all', 'after'] and node_id in visited_downstream_edges:
                cfg["classes"] = "base-edge edge-downstream"
            else:
                cfg["classes"] = "base-edge faded-edge"
        elif node_id.startswith("grp_") or node_id in ['4392351365515c6d', '6283cfcedbf60137']:
            cfg["classes"] = "group-box"
        else:
            if node_id == active_id:
                cfg["classes"] = "process-node node-focused"
            elif filter_mode in ['all', 'before'] and node_id in visited_upstream_nodes:
                cfg["classes"] = "process-node node-upstream"
            elif filter_mode in ['all', 'after'] and node_id in visited_downstream_nodes:
                cfg["classes"] = "process-node node-downstream"
            else:
                cfg["classes"] = "process-node faded-node"
                
        updated_elements.append(cfg)

    # UI do Painel Lateral Customizado por Filtro
    selected_node = next(x['data'] for x in elements if x['data']['id'] == active_id)
    def get_label(component_id):
        return next((x['data'].get('label', component_id) for x in elements if x['data']['id'] == component_id), component_id)

    # Monta os blocos informativos baseado nas escolhas
    upstream_block = html.Div(style={"marginBottom": "20px"}, children=[
        html.Div(style={"display": "flex", "alignItems": "center", "gap": "8px", "marginBottom": "8px"}, children=[
            html.Div(style={"width": "8px", "height": "8px", "borderRadius": "50%", "backgroundColor": "#2563eb"}),
            html.Label(f"Insumos Requeridos ({len(visited_upstream_nodes)} predecessores)", style={"fontSize": "11px", "textTransform": "uppercase", "color": "#2563eb", "fontWeight": "600"})
        ]),
        html.Div(style={"backgroundColor": "#ffffff", "padding": "10px 15px", "borderRadius": "8px", "border": "1px solid #e2e8f0", "maxHeight": "140px", "overflowY": "auto"}, children=[
            html.Ul([html.Li(get_label(u), style={"margin": "4px 0", "fontSize": "12px", "color": "#334155"}) for u in visited_upstream_nodes] if visited_upstream_nodes else [html.Li("Este card é a raiz inicial (Origem absoluta).", style={"fontStyle":"italic", "fontSize": "12px", "color": "#94a3b8"})], style={"paddingLeft": "15px", "margin": 0})
        ])
    ]) if filter_mode in ['all', 'before'] else None

    downstream_block = html.Div(children=[
        html.Div(style={"display": "flex", "alignItems": "center", "gap": "8px", "marginBottom": "8px"}, children=[
            html.Div(style={"width": "8px", "height": "8px", "borderRadius": "50%", "backgroundColor": "#16a34a"}),
            html.Label(f"Desdobramentos e Impactos ({len(visited_downstream_nodes)} sucessores)", style={"fontSize": "11px", "textTransform": "uppercase", "color": "#16a34a", "fontWeight": "600"})
        ]),
        html.Div(style={"backgroundColor": "#ffffff", "padding": "10px 15px", "borderRadius": "8px", "border": "1px solid #e2e8f0", "maxHeight": "140px", "overflowY": "auto"}, children=[
            html.Ul([html.Li(get_label(d), style={"margin": "4px 0", "fontSize": "12px", "color": "#334155"}) for d in visited_downstream_nodes] if visited_downstream_nodes else [html.Li("Etapa final. Não existem entregas posteriores.", style={"fontStyle":"italic", "fontSize": "12px", "color": "#94a3b8"})], style={"paddingLeft": "15px", "margin": 0})
        ])
    ]) if filter_mode in ['all', 'after'] else None

    panel_jsx = html.Div([
        html.Div(style={"backgroundColor": "#ffffff", "padding": "15px", "borderRadius": "8px", "marginBottom": "20px", "border": "1px solid #e2e8f0", "borderLeft": "4px solid #0284c7"}, children=[
            html.Label("Foco Selecionado", style={"fontSize": "10px", "textTransform": "uppercase", "color": "#64748b", "fontWeight": "600"}),
            html.H4(selected_node.get('label', active_id), style={"color": "#0f172a", "margin": "2px 0 0 0", "fontSize": "14px", "fontWeight": "600"}),
            html.P(selected_node.get('full_text', '').replace("[[", "").replace("]]", ""), style={"fontSize": "11px", "color": "#475569", "marginTop": "6px", "lineHeight": "1.4"})
        ]),
        upstream_block,
        downstream_block
    ])
    
    return updated_elements, panel_jsx

if __name__ == '__main__':
    app.run(debug=True)