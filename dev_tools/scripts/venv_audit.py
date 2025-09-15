import json, subprocess, networkx as nx, plotly.graph_objects as go
import pandas as pd

# Captura pacotes instalados
pip_list = subprocess.check_output(["pip", "list", "--format=json"], text=True)
pacotes = pd.DataFrame(json.loads(pip_list))

# Captura conflitos
pip_check = subprocess.run(["pip", "check"], capture_output=True, text=True)
conflitos = pip_check.stdout.splitlines()

# Cria grafo de dependências (simplificado)
G = nx.DiGraph()
for _, row in pacotes.iterrows():
    G.add_node(row["name"], version=row["version"])

# Adiciona arestas para pacotes conflitantes (exemplo visual)
for linha in conflitos:
    if "requires" in linha:
        parts = linha.split(" requires ")
        pkg, dep = parts[0], parts[1]
        G.add_edge(pkg.strip(), dep.split()[0].strip())

# Plotly para gráfico interativo
pos = nx.spring_layout(G, seed=42)
edge_x, edge_y = [], []
for edge in G.edges():
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    edge_x += [x0, x1, None]
    edge_y += [y0, y1, None]

edge_trace = go.Scatter(
    x=edge_x, y=edge_y,
    line=dict(width=1, color='#888'),
    hoverinfo='none',
    mode='lines'
)

node_x, node_y, node_text, node_color = [], [], [], []
for node in G.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)
    version = G.nodes[node].get('version', 'desconhecida')  # correção aqui
    node_text.append(f"{node} ({version})")
    node_color.append('red' if any(node in c for c in conflitos) else 'blue')


node_trace = go.Scatter(
    x=node_x, y=node_y,
    mode='markers+text',
    hoverinfo='text',
    marker=dict(color=node_color, size=20),
    text=node_text,
    textposition="top center"
)

fig = go.Figure(data=[edge_trace, node_trace])
fig.update_layout(title="Gráfico de Dependências da Venv", showlegend=False)
fig.write_html("venv_dependency_report.html")

# Relatório HTML completo
with open("venv_dependency_report.html", "a") as f:
    f.write(f"<p>Total de pacotes: {len(pacotes)}</p>")
    f.write("<ul>")
    for c in conflitos:
        f.write(f"<li style='color:red'>{c}</li>")
    f.write("</ul>")

print("Relatório gerado: venv_dependency_report.html")
