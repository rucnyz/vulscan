import importlib.util
import os
import ast
from typing import Any, Optional

def validate_plugin_code(plugin_code: str) -> bool:
    try:
        # Parse the code into AST
        tree = ast.parse(plugin_code)
        
        # Check for forbidden elements
        for node in ast.walk(tree):
            # Prevent imports
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                return False
            # Prevent exec, eval, and system calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['exec', 'eval', 'os', 'system']:
                        return False
            # Prevent accessing dangerous attributes
            if isinstance(node, ast.Attribute):
                if node.attr.startswith('__'):
                    return False
        return True
    except Exception:
        return False

def load_user_plugin(plugin_name: str, plugin_code: str) -> bool:
    # Validate plugin name
    if not plugin_name.isalnum():
        return False
    
    # Validate plugin code
    if not validate_plugin_code(plugin_code):
        return False
    
    try:
        # Create sandbox directory
        plugin_dir = "sandbox_plugins"
        if not os.path.exists(plugin_dir):
            os.makedirs(plugin_dir)
        
        # Write validated plugin code
        plugin_path = os.path.join(plugin_dir, f"{plugin_name}.py")
        with open(plugin_path, 'w') as f:
            f.write(plugin_code)
        
        # Load plugin in restricted environment
        spec = importlib.util.spec_from_file_location(
            plugin_name,
            plugin_path,
            submodule_search_locations=[]
        )
        module = importlib.util.module_from_spec(spec)
        
        # Restrict available builtins
        safe_builtins = {
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'len': len,
            'range': range,
        }
        module.__dict__['__builtins__'] = safe_builtins
        
        spec.loader.exec_module(module)
        return True
        
    except Exception as e:
        print(f"Failed to load plugin: {e}")
        return False

def execute_plugin_function(plugin_name: str, function_name: str, *args) -> Optional[Any]:
    # Validate inputs
    if not plugin_name.isalnum() or not function_name.isalnum():
        return None
    
    try:
        # Load plugin from sandbox
        plugin_path = os.path.join("sandbox_plugins", f"{plugin_name}.py")
        if not os.path.exists(plugin_path):
            return None
            
        spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
        module = importlib.util.module_from_spec(spec)
        
        # Apply safe builtins
        safe_builtins = {
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'len': len,
            'range': range,
        }
        module.__dict__['__builtins__'] = safe_builtins
        
        spec.loader.exec_module(module)
        
        if hasattr(module, function_name):
            func = getattr(module, function_name)
            return func(*args)
        return None
        
    except Exception:
        return None