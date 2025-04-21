import ChironAST.ChironAST as ChironAST



class Stack:
    def __init__(self):
        self.items = []

    def push(self, value):
        self.items.append(value)

    def pop(self):
        return self.items.pop() if self.items else None

    def is_empty(self):
        return len(self.items) == 0

    def peek(self):
        return self.items[-1] if self.items else None



def rename_vars_in_expr(x, idx, expr, rename_map):
    """
    Recursively rename variables in an expression (arithmetic or boolean).
    """
    if isinstance(expr, ChironAST.Var):
        sup = expr.__str__()
        try:
            version = rename_map[sup].peek().__str__()
        except KeyError:
            version = "-1"  # or any default value you'd like to use

        return ChironAST.Var(sup + "_" + version)
    elif isinstance(expr, ChironAST.Num):
        return expr
    elif isinstance(expr, ChironAST.UnaryArithOp):
        return ChironAST.UnaryArithOp(rename_vars_in_expr(x, idx, expr.expr, rename_map), expr.symbol)
    elif isinstance(expr, ChironAST.BinArithOp):
        return ChironAST.BinArithOp(rename_vars_in_expr(x, idx, expr.lexpr, rename_map),
                          rename_vars_in_expr(x, idx, expr.rexpr, rename_map),
                          expr.symbol)
    elif isinstance(expr, ChironAST.BinCondOp):
        return ChironAST.BinCondOp(rename_vars_in_expr(x, idx, expr.lexpr, rename_map),
                         rename_vars_in_expr(x, idx, expr.rexpr, rename_map),
                         expr.symbol)
    elif isinstance(expr, ChironAST.NOT):
        return ChironAST.NOT(rename_vars_in_expr(x, idx, expr.expr, rename_map))
    elif isinstance(expr, ChironAST.PenStatus) or isinstance(expr, ChironAST.BoolTrue) or isinstance(expr, ChironAST.BoolFalse):
        return expr
    else:
        raise NotImplementedError(f"Expression type {type(expr)} not handled.")



def rename_rhs_variables(x, instr_list, rename_map, c, old_lhs):
    """
    Rename variables only in RHS of specific instruction types.
    """
    idx = 0
    updated_instr = []
    for instr, idx_temp in instr_list:
        if isinstance(instr, ChironAST.AssignmentCommand):
                # modified1 = ChironAST.AssignmentCommand(instr.lvar, rename_vars_in_expr(instr.rexpr, rename_map))
                modified_rhs = rename_vars_in_expr(x, idx, instr.rexpr, rename_map)
                
                # sup = instr.lvar.__str__()
                sup_assign = old_lhs[x][idx]
                i = c[sup_assign]
                modified_lhs = ChironAST.Var(sup_assign + "_" + i.__str__())
                rename_map[sup_assign].push(i)
                c[sup_assign] = i+1
                updated_instr.append((ChironAST.AssignmentCommand(modified_lhs, modified_rhs), idx))


        elif isinstance(instr, ChironAST.ConditionCommand):
            updated_instr.append(
                (ChironAST.ConditionCommand(rename_vars_in_expr(x, idx, instr.cond, rename_map)), idx)
            )
        elif isinstance(instr, ChironAST.AssertCommand):
            updated_instr.append(
                (ChironAST.AssertCommand(rename_vars_in_expr(x, idx, instr.cond, rename_map)), idx)
            )
        elif isinstance(instr, ChironAST.MoveCommand):
            updated_instr.append(
                (ChironAST.MoveCommand(instr.direction, rename_vars_in_expr(x, idx, instr.expr, rename_map)), idx)
            )
        elif isinstance(instr, ChironAST.GotoCommand):
            updated_instr.append(
                (ChironAST.GotoCommand(rename_vars_in_expr(x, idx, instr.xcor, rename_map),
                            rename_vars_in_expr(x, idx, instr.ycor, rename_map)), idx)
            )
        elif isinstance(instr, ChironAST.PhiFunction):
            # sup = instr.var.__str__()
            sup_phi = old_lhs[x][idx]
            i = c[sup_phi]
            modified_lhs = ChironAST.Var(sup_phi + "_" + i.__str__())
            rename_map[sup_phi].push(i)
            c[sup_phi] = i+1
            updated_instr.append((ChironAST.PhiFunction(modified_lhs), idx))
        else:
            updated_instr.append((instr, idx))
        
        idx = idx + 1
    return updated_instr



def set_ith_element(lst, i, x):
    if i < len(lst):
        lst[i] = x
    else:
        # Extend with 0s until we reach index i
        lst.extend([0] * (i - len(lst)))
        lst.append(x)



def search_renaming_variables(x, dom_tree, s, c, cfg, cfg_pred_dict, old_lhs):
    x.instrlist = rename_rhs_variables(x, x.instrlist, s, c, old_lhs)            

    for y in list(cfg.nxgraph.successors(x)):
        sup = cfg_pred_dict[y]
        j = sup.index(x)
        idx = 0
        for instr, idx_temp in y.instrlist:
            if(isinstance(instr, ChironAST.PhiFunction)):
                # instr.rhs_list
                old_var = old_lhs[y][idx]
                set_ith_element(instr.rhs_list, j, s[old_var].peek())
            idx = idx + 1
        
    if (list(dom_tree.successors(x))):
        for y in list(dom_tree.successors(x)):
            search_renaming_variables(y, dom_tree, s, c, cfg, cfg_pred_dict, old_lhs)

    curr_old_lhs_list = old_lhs[x]
    for i in curr_old_lhs_list:
        if (i != -1):
            s[i].pop()



def renaming_variables(var_set, cfg, dom_tree):
    c = {key:0 for key in var_set}
    s = {key: Stack() for key in var_set}

    old_lhs = dict()
    for bb in cfg.nxgraph.nodes():
        old_lhs[bb] = []
        for instr, idx in bb.instrlist:
            if(isinstance(instr, ChironAST.AssignmentCommand)):
                old_lhs[bb].append(instr.lvar.__str__())
            elif(isinstance(instr, ChironAST.PhiFunction)):
                old_lhs[bb].append(instr.var.__str__())
            else:
                old_lhs[bb].append(-1)
    
    cfg_adj_dict = {node: list(cfg.nxgraph.adj[node]) for node in cfg.nxgraph.nodes()}
    cfg_pred_dict = {node: list(cfg.nxgraph.predecessors(node)) for node in cfg.nxgraph.nodes()}

    for item in old_lhs.keys():
        print(item.name + "->" + old_lhs[item].__str__())
    # for item in cfg_adj_dict.keys():
        # print(item.__str__() + "->" + cfg_adj_dict[item].__str__())
    # for item in cfg_pred_dict.keys():
        # print(item.__str__() + "->" + cfg_adj_dict[item].__str__())
    
    roots = [node for node in dom_tree.nodes if dom_tree.in_degree(node) == 0]
    if len(roots) == 1:
        root = roots[0]
        search_renaming_variables(root, dom_tree, s, c, cfg, cfg_pred_dict, old_lhs)
    else:
        print("Warning: Tree has", len(roots), "roots:", roots)