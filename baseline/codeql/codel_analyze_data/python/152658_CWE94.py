import ast
def run_python_snippet(python_snippet: str):
    exec(python_snippet)
    return None