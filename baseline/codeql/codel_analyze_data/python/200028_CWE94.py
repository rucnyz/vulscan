import importlib.util
import os

def load_user_plugin(plugin_name: str, plugin_code: str) -> bool:
    try:
        # Create plugin directory if not exists
        plugin_dir = "user_plugins"
        if not os.path.exists(plugin_dir):
            os.makedirs(plugin_dir)
        
        # Write plugin code to a new Python file
        plugin_path = os.path.join(plugin_dir, f"{plugin_name}.py")
        with open(plugin_path, 'w') as f:
            f.write(plugin_code)
        
        # Dynamically load the plugin
        spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Store the loaded plugin
        globals()[f"plugin_{plugin_name}"] = module
        return True
        
    except Exception as e:
        print(f"Failed to load plugin: {e}")
        return False

def execute_plugin_function(plugin_name: str, function_name: str, *args):
    plugin = globals().get(f"plugin_{plugin_name}")
    if plugin and hasattr(plugin, function_name):
        func = getattr(plugin, function_name)
        return func(*args)
    return None