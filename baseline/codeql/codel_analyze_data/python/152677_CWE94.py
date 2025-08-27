import re
def handle_user_expression(expression: str):
    if re.match("^[0-9+\-*/\s]+$", expression):
        try:
            result = eval(expression)
        except Exception as e:
            raise ValueError(f"Error processing expression: {str(e)}")
    else:
        raise ValueError("Invalid expression")
    return result