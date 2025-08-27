import re
from typing import List, Any

def process_dynamic_command(cmd_str: str, allowed_commands: List[str]) -> str:
    # Define command patterns and their handlers
    command_handlers = {
        'print': lambda x: str(x),
        'upper': lambda x: str(x).upper(),
        'lower': lambda x: str(x).lower(),
        'length': lambda x: str(len(str(x)))
    }
    
    # Validate command format
    cmd_pattern = re.compile(r'^([a-zA-Z_][a-zA-Z0-9_]*)\((.*)\)$')
    match = cmd_pattern.match(cmd_str)
    
    if not match:
        return "Invalid command format"
    
    cmd_name, args = match.groups()
    
    # Verify command is allowed
    if cmd_name not in allowed_commands or cmd_name not in command_handlers:
        return "Command not allowed"
    
    try:
        # Process arguments safely
        args = args.strip("\"\\' ")
        # Execute the command using predefined handler
        result = command_handlers[cmd_name](args)
        return result
    except Exception as e:
        return f"Error executing command: {e}"