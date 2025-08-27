from typing import Dict, Any
import ast
import operator

def execute_math_formula(formula: str) -> float:
    # Define safe operations
    safe_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
    }
    
    def eval_expr(node: ast.AST) -> float:
        if isinstance(node, ast.Num):
            return float(node.n)
        elif isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in safe_operators:
                raise ValueError("Unsupported operation")
            left = eval_expr(node.left)
            right = eval_expr(node.right)
            return safe_operators[op_type](left, right)
        else:
            raise ValueError("Invalid expression type")
    
    try:
        parsed = ast.parse(formula, mode='eval')
        result = eval_expr(parsed.body)
        return float(result)
    except Exception as e:
        print(f"Error in formula: {e}")
        return 0.0