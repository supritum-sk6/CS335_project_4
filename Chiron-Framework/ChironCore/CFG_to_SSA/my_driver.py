import CFG_to_SSA.myfile as myfile
import networkx as nx
from networkx.drawing.nx_agraph import to_agraph
import ChironAST.ChironAST as ChironAST
from queue import Queue



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



def compute_dominance_frontiers(cfg, dom_tree):
    """
    Computes the dominance frontiers for each node in the control flow graph using
    a bottom-up traversal of the dominator tree.
    
    Parameters:
        cfg (ChironCFG): The control flow graph as a ChironCFG object.
        dom_tree (nx.DiGraph): The dominator tree as a directed graph.
        
    Returns:
        dict: A dictionary where keys are nodes and values are sets representing their dominance frontiers.
    """
    graph = cfg.nxgraph
    idom = nx.immediate_dominators(graph, cfg.entry)
    
    dominance_frontier = {node: set() for node in graph.nodes()}
    
    # Perform a bottom-up traversal of the dominator tree
    postorder = list(nx.dfs_postorder_nodes(dom_tree, source=cfg.entry))
    
    for node in postorder:
        # Compute DF_local(X)
        for successor in graph.successors(node):
            if idom[successor] != node:
                dominance_frontier[node].add(successor)
        
        # Compute DF_up(Z)
        for child in dom_tree.successors(node):
            for y in dominance_frontier[child]:
                if idom[y] != node:
                    dominance_frontier[node].add(y)
    
    return dominance_frontier



def dump_dominator_tree(dom_tree, filename="dominator_tree"):
    """
    Generates a PNG image of the dominator tree.
    
    Parameters:
        dom_tree (nx.DiGraph): The dominator tree as a directed graph.
        filename (str): The filename for the output image (default: "dominator_tree").
    """
    # labels = {}
    # for node in dom_tree:
    #     labels[node] = node.label()
    #     # print("bb name : " + node.name + ", ir Id = " + str(node.irID))

    # dom_tree = nx.relabel_nodes(dom_tree, labels)
    A = to_agraph(dom_tree)
    A.layout('dot')
    A.draw(filename + ".png")



def variable_list(ir):
    var_set = set()
    for idx, item in enumerate(ir):
        if(isinstance(item[0], ChironAST.AssignmentCommand)):
            curr_var = item[0].lvar.varname
            # if(curr_var not in var_set):
            # print(item[0])
            var_set.add(curr_var)
    return var_set



def nodes_where_each_var_occur(var_set, cfg):
    var_bb_map = {key: set() for key in var_set}
    basic_blocks = cfg.nxgraph.nodes()
    for curr_block in basic_blocks:
        instrlist = curr_block.instrlist
        for idx, item in enumerate(instrlist):
            if(isinstance(item[0], ChironAST.AssignmentCommand)):
                curr_var = item[0].lvar.varname
                var_bb_map[curr_var].add(curr_block)
    return var_bb_map



def var_identify_nodes_requiring_phi_functions_map(var_set, var_bb_map, cfg, dom_frontiers):
    var_phi_nodes_map = {key:[] for key in var_set}
    iteration_count = 0
    basic_blocks = cfg.nxgraph.nodes()
    has_already = {key:0 for key in basic_blocks}
    work = {key:0 for key in basic_blocks}

    w = Queue()

    for v in var_set:
        iteration_count = iteration_count + 1
        for x in var_bb_map[v]:
            work[x] = iteration_count
            w.put(x)
        
        while(not w.empty()):
            x = w.get()
            for y in dom_frontiers[x]:
                if(has_already[y] < iteration_count):
                    var_phi_nodes_map[v].append(y)
                    has_already[y] = iteration_count
                    if(work[y] < iteration_count):
                        work[y] = iteration_count
                        w.put(y)
    return var_phi_nodes_map



def build_SSA(ir, cfg):
    myfile.print_ir(ir)
    myfile.print_basic_blocks(cfg)
    myfile.print_edges(cfg)

    dom_tree = compute_dominator_tree(cfg)
    myfile.print_dominator_tree(dom_tree)
    dump_dominator_tree(dom_tree)

    dom_frontiers = compute_dominance_frontiers(cfg, dom_tree)
    myfile.print_dominance_frontiers(dom_frontiers)

    var_set = variable_list(ir)
    # print(var_set)
    print("\n\nvar_set...")
    for item in var_set:
        print(item)
    
    var_bb_map = nodes_where_each_var_occur(var_set, cfg)
    print("\n\nvar_bb_map...")
    for key, obj_set in var_bb_map.items():
        field_values = [obj.name for obj in obj_set]  # Extract 'field' attribute
        print(f"{key}: {field_values}")
    
    var_phi_nodes_map = var_identify_nodes_requiring_phi_functions_map(var_set, var_bb_map, cfg, dom_frontiers)
    print("\n\nvar_phi_nodes_map...")
    for key, obj_set in var_phi_nodes_map.items():
        field_values = [obj.name for obj in obj_set]  # Extract 'field' attribute
        print(f"{key}: {field_values}")