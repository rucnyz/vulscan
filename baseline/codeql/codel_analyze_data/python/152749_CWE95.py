
def evaluate_user_code(code_string: str) -> str:
    try:
        import ast
        parsed_script = ast.parse(code_string, mode="eval")
        allowed_nodes_types = (
            ast.Expression,
            ast.BinOp,
            ast.UnaryOp,
            ast.operator,
            ast.Constant,
            ast.Str,
            ast.Num,
            ast.Compare,
            ast.BoolOp
        )

        # Check if all nodes in the AST are valid
        if any(not isinstance(node, allowed_nodes_types) for node in ast.walk(parsed_script)):
            result = 'Execution Blocked!'
        else:
            compiled_script = compile(parsed_script, filename="", mode="eval")
            result = eval(compiled_script)
    except Exception:
        return "Execution Blocked!"
    return str(result)