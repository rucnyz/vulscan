
def evaluate_user_code(code_string: str) -> str:
    try:
        result = eval(code_string)
    except Exception:
        return "Execution Blocked!"
    return str(result)