import cfg.cfgBuilder as cfgB
import cfg.ChironCFG as cfgC



def print_ir(ir):
    """
    Function to print IR instructions in a formatted way.
    
    Each instruction is printed with its corresponding index.
    """
    currIdx = 0
    while currIdx < len(ir):
        instruction, index = ir[currIdx][0], currIdx
        print(f"Instruction {index}: {instruction} [{ir[currIdx][1]}]")
        currIdx += 1



def print_basic_blocks(cfg):
    """
    Prints the basic blocks in a structured order:
    - First, the "START" block.
    - Then, blocks in ascending order of their names.
    - Finally, the "END" block.

    Parameters:
    cfg (ChironCFG): The control flow graph object.
    """
    print("\n=== Ordered Basic Blocks in CFG ===\n")

    # Extract blocks
    start_block = None
    end_block = None
    numbered_blocks = []

    for block in cfg:
        if block.name == "START":
            start_block = block
        elif block.name == "END":
            end_block = block
        else:
            try:
                block_number = int(block.name)
                numbered_blocks.append((block_number, block))
            except ValueError:
                print(f"Warning: Unexpected block name '{block.name}' (Skipping)")

    # Sort numbered blocks by their numerical name
    numbered_blocks.sort()

    # Print in order: START -> Sorted Blocks -> END
    ordered_blocks = [start_block] + [b[1] for b in numbered_blocks] + [end_block]

    for block in ordered_blocks:
        if block:
            print(f"Basic Block: {block.name}")
            if block.instrlist:
                for instr, idx in block.instrlist:
                    print(f"  - {instr} (IR Index: {idx})")
            else:
                print("  - [Empty Block]")
            print("\n" + "-" * 30 + "\n")  # Separator



def print_edges(cfg):
    edges_list = cfg.edges()
    edges_list = list(edges_list(data=True))

    print(f"    {'From':<8}{'To':<8}{'Label'}")
    print("-" * 30)
    print("-" * 30)

    i=1
    for u, v, attr in edges_list:
        # label = attr.get("label", "None")
        print(f"{i}.  {u.name:<8}{v.name:<8}{attr}")
        i = i+1



def print_dominator_tree(dom_tree):
    """
    Prints the dominator tree in a readable format.
    
    Parameters:
        dom_tree (nx.DiGraph): The dominator tree as a directed graph.
    """
    for parent in dom_tree.nodes():
        children = list(dom_tree.successors(parent))
        print(f"{parent} -> {', '.join(map(str, children))}" if children else f"{parent} -> []")



def print_dominance_frontiers(dominance_frontier):
    """
    Prints the dominance frontiers in a readable format.
    
    Parameters:
        dominance_frontier (dict): A dictionary where keys are nodes and values are sets representing their dominance frontiers.
    """
    for node, frontier in dominance_frontier.items():
        print(f"DF({node}) -> {', '.join(map(str, frontier)) if frontier else '∅'}")