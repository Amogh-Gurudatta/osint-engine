import asyncio
# pyrefly: ignore [missing-import]
from pyvis.network import Network

from ingestion import fetch_osint_data
from graph_engine import build_graph, resolve_identities

def visualize_graph(G, output_file):
    """
    Exports the NetworkX graph to an interactive HTML file using Pyvis.
    """
    # Initialize a Pyvis network with a dark theme
    net = Network(height='100vh', width='100%', bgcolor='#1a1a1a', font_color='white', directed=False)
    
    # Manual Translation of Nodes
    for node_id, attrs in G.nodes(data=True):
        node_type = attrs.get('type')
        if node_type == 'username':
            color = '#00ffcc'  # cyan
        elif node_type == 'email':
            color = '#ff3366'  # pink
        elif node_type == 'location':
            color = '#ffcc00'  # yellow
        else:
            color = '#ffffff'  # default fallback
            
        # Add node with styling
        net.add_node(node_id, label=str(node_id), title=f"Type: {node_type}", color=color)
        
    # Manual Translation of Edges
    for u, v, attrs in G.edges(data=True):
        if attrs.get('label') == 'IS_SAME_PERSON':
            color = '#ff0000'
            width = 4
            title = 'IS_SAME_PERSON'
        elif attrs.get('label') == 'POSSIBLE_MATCH':
            color = attrs.get('color', '#ffa500')
            width = 2
            title = f"POSSIBLE_MATCH"
        else:
            color = attrs.get('color', '#555555')
            width = 1
            title = 'Linked Data'
            
        net.add_edge(u, v, color=color, width=width, title=title)
        
    # Enable repulsion physics
    net.repulsion(node_distance=150, central_gravity=0.2, spring_length=200)
    
    # Save the network
    net.write_html(output_file)

async def run_pipeline():
    """
    Orchestrates the live data ingestion, graph construction, resolution, and visualization.
    """
    target = input("\nEnter target username to investigate: ").strip()
    if not target:
        print("Username cannot be empty.")
        return
        
    print(f"[*] Fetching live OSINT footprints for '{target}'...")
    data = await fetch_osint_data(target)
    
    if not data:
        print(f"[-] No data found for '{target}' across public endpoints.")
        return
        
    print("[*] Building initial graph topology...")
    G = build_graph(data)
    
    print(f"    - Nodes: {G.number_of_nodes()}")
    print(f"    - Edges: {G.number_of_edges()}")
    
    print("[*] Executing deterministic identity resolution algorithm...")
    resolved_G = resolve_identities(G)
    
    print(f"    - Resolved Nodes: {resolved_G.number_of_nodes()}")
    print(f"    - Resolved Edges: {resolved_G.number_of_edges()}")
    
    output_file = 'output.html'
    print(f"[*] Exporting interactive visualization to '{output_file}'...")
    visualize_graph(resolved_G, output_file)
    
    print(f"\n[+] SUCCESS! The resolution engine has finished. Open '{output_file}' in your browser to explore the graph.")

if __name__ == '__main__':
    asyncio.run(run_pipeline())
