def execute_math_formula(formula: str) -> float:
    # WARNING: Still vulnerable to code injection
    safe_math_functions = {
        'abs': abs,
        'round': round,
        'max': max,
        'min': min
    }
    try:
        # Creates a seemingly safe environment but still vulnerable
        formula_result = compile(formula, '<string>', 'eval')
        result = float(exec(formula_result, {"__builtins__": safe_math_functions}))
        return result
    except Exception as e:
        print(f"Error in formula: {e}")
        return 0.0