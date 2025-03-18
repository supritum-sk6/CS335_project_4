import CFG_to_SSA.myfile as myfile
import networkx as nx



def compute_dominator_tree(cfg):
    """
    Computes the dominator tree for a given ChironCFG object.
    
    Parameters:
        cfg (ChironCFG): The control flow graph as a ChironCFG object.
        
    Returns:
        nx.DiGraph: The dominator tree as a directed graph.
    """
    # Extract the underlying NetworkX DiGraph
    graph = cfg.nxgraph
    entry_node = cfg.entry  # Assuming entry node is set in ChironCFG

    # Ensure the entry node exists in the graph
    if entry_node not in graph:
        raise ValueError(f"Entry node '{entry_node}' is not present in the graph.")
    
    # Compute the dominator tree using NetworkX's immediate dominators function
    idom = nx.immediate_dominators(graph, entry_node)
    
    # Construct the dominator tree
    dom_tree = nx.DiGraph()
    for node, dom in idom.items():
        if node != entry_node:  # Exclude the root from being its own child
            dom_tree.add_edge(dom, node)
    
    return dom_tree



def build_SSA(ir, cfg):
    myfile.print_ir(ir)
    myfile.print_basic_blocks(cfg)
    myfile.print_edges(cfg)

    dom_tree = compute_dominator_tree(cfg)
    myfile.print_dominator_tree(dom_tree)