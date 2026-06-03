import networkx as nx
import asyncio
import itertools
from difflib import SequenceMatcher

# Import the ingestion function
from ingestion import fetch_osint_data

def build_graph(data_list):
    """
    Build a relational network graph where data values are nodes,
    and edges connect values found in the same mock footprint.
    """
    G = nx.Graph()
    
    for profile in data_list:
        username = profile.get("username")
        email = profile.get("email")
        location = profile.get("location")
        
        # Add nodes if they don't exist and they are not None
        if username is not None:
            if not G.has_node(username):
                G.add_node(username, type='username')
                
        if email is not None:
            if not G.has_node(email):
                G.add_node(email, type='email')
            # Link username to email
            if username is not None:
                G.add_edge(username, email)
                
        if location is not None:
            if not G.has_node(location):
                G.add_node(location, type='location')
            # Link username to location
            if username is not None:
                G.add_edge(username, location)
                
    return G

def resolve_identities(G):
    """
    Execute a deterministic matching algorithm to link identities.
    If an email node has 2+ distinct username neighbors, they are the same person.
    """
    # Find all nodes where type='email'
    email_nodes = [n for n, attr in G.nodes(data=True) if attr.get('type') == 'email']
    
    for email in email_nodes:
        # Find all neighboring nodes where type='username'
        username_neighbors = [
            neighbor for neighbor in G.neighbors(email) 
            if G.nodes[neighbor].get('type') == 'username'
        ]
        
        # If 2 or more distinct usernames, create direct edges between them
        if len(username_neighbors) >= 2:
            for u1, u2 in itertools.combinations(username_neighbors, 2):
                G.add_edge(u1, u2, label='IS_SAME_PERSON', weight=100)
                
    # Phase 2: Fuzzy Username Resolution
    username_nodes = [n for n, attr in G.nodes(data=True) if attr.get('type') == 'username']
    
    for u1, u2 in itertools.combinations(username_nodes, 2):
        ratio = SequenceMatcher(None, str(u1).lower(), str(u2).lower()).ratio()
        if ratio > 0.75:
            # Check if an edge already exists to prevent overwriting exact matches
            if not G.has_edge(u1, u2):
                G.add_edge(u1, u2, label='POSSIBLE_MATCH', weight=50, color='#ffa500')
                
    return G

if __name__ == '__main__':
    # Run the async fetch and build the graph
    target = input("Enter target username for test: ")
    data = asyncio.run(fetch_osint_data(target))
    
    # Step 1: Construct Graph
    G = build_graph(data)
    
    # Step 2: Resolve Identities
    G = resolve_identities(G)
    
    # Step 3: Verification Output
    print(f"Total number of nodes: {G.number_of_nodes()}")
    print(f"Total number of edges: {G.number_of_edges()}")
    
    print("\nVerified Identity Matches (Grouped by Cluster):")
    match_found = False
    
    # Use networkx connected components to find all nodes linked together
    for component in nx.connected_components(G):
        # Extract only the username nodes from the connected component
        usernames = [n for n in component if G.nodes[n].get('type') == 'username']
        if len(usernames) > 1:
            print(f"MATCH FOUND Cluster: {', '.join(usernames)}")
            match_found = True
            
    if not match_found:
        print("No matches found.")
