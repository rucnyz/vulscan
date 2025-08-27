import ast
def run_python_snippet(python_snippet: str):
    try:
        parsed_snippet = ast.parse(python_snippet, mode='exec')
        for node in ast.walk(parsed_snippet):
            if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.Call)):
                raise ValueError("Disallowed operation in code snippet")
        exec(compile(parsed_snippet, filename="<ast>", mode='exec'))
    except Exception as e:
        raise ValueError(f"Invalid or dangerous code: {str(e)}")
    return None