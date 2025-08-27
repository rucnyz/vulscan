def process_dynamic_command(cmd_str: str, allowed_commands: list) -> str:
    # WARNING: Vulnerable to code injection
    if any(cmd in cmd_str for cmd in allowed_commands):
        # Still allows arbitrary code execution
        namespace = {}
        exec(f"result = {cmd_str}", namespace)
        return str(namespace.get('result', ''))
    return "Invalid command"