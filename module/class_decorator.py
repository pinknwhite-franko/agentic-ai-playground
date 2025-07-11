import inspect
from typing import get_type_hints
import config

def get_json_type(py_type):
    """
    Maps Python types to JSON schema types.

    Parameters:
        py_type (object): The Python type to map.

    Returns:
        str: The corresponding JSON schema type.
    """
    if py_type in [str]:
        return "string"
    elif py_type in [int]:
        return "integer"
    elif py_type in [float]:
        return "number"
    elif py_type in [bool]:
        return "boolean"
    elif py_type in [list, tuple]:
        return "array"
    elif py_type in [dict]:
        return "object"
    else:
        return "string"

def register_tool(tool_name=None, description=None, 
                 parameters_override=None, terminal=False, tags=None):
    """
    Registers a function as an agent tool.

    Parameters:
        tool_name (str, optional): The name of the tool. Defaults to the function name.
        description (str, optional): Description of the tool. Defaults to the function's docstring.
        parameters_override (dict, optional): Override for the argument schema. Defaults to dynamically inferred schema.
        terminal (bool, optional): Whether the tool is terminal. Defaults to False.
        tags (List[str], optional): List of tags to associate with the tool.
        
    Returns:
        function: The decorated function with tool registration.
    """
    def decorator(func):
        # Extract all metadata from the function
        metadata = get_tool_metadata(
            func=func,
            tool_name=tool_name,
            description=description,
            parameters_override=parameters_override,
            terminal=terminal,
            tags=tags
        )
        
        # Register in our global tools dictionary
        config.TOOLS[metadata["tool_name"]] = {
            "description": metadata["description"],
            "parameters": metadata["parameters"],
            "function": metadata["function"],
            "terminal": metadata["terminal"],
            "tags": metadata["tags"]
        }
        
        # Also maintain a tag-based index
        for tag in metadata["tags"]:
            if tag not in config.TOOLS_BY_TAG:
                config.TOOLS_BY_TAG[tag] = []
            config.TOOLS_BY_TAG[tag].append(metadata["tool_name"])
        
        return func
    return decorator


def get_tool_metadata(func, tool_name=None, description=None, 
                     parameters_override=None, terminal=False, tags=None):
    """
    Extracts metadata for a function to use in tool registration.

    Parameters:
        func (function): The function to extract metadata from.
        tool_name (str, optional): The name of the tool. Defaults to the function name.
        description (str, optional): Description of the tool. Defaults to the function's docstring.
        parameters_override (dict, optional): Override for the argument schema. Defaults to dynamically inferred schema.
        terminal (bool, optional): Whether the tool is terminal. Defaults to False.
        tags (List[str], optional): List of tags to associate with the tool.

    Returns:
        dict: A dictionary containing metadata about the tool, including description, args schema, and the function.
    """
    
    # Use function name if no tool_name provided
    tool_name = tool_name or func.__name__
    
    # Use docstring if no description provided
    description = description or (func.__doc__.strip() 
                                if func.__doc__ else "No description provided.")
    
    # If no parameter override, analyze the function
    if parameters_override is None:
        signature = inspect.signature(func)
        type_hints = get_type_hints(func)
        
        # Build JSON schema for arguments
        args_schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        # Examine each parameter
        for param_name, param in signature.parameters.items():
            # Skip special parameters
            if param_name in ["action_context", "action_agent"]:
                continue

            # Convert Python types to JSON schema types
            param_type = type_hints.get(param_name, str)
            param_schema = {
                "type": get_json_type(param_type)
            }
            
            args_schema["properties"][param_name] = param_schema
            
            # If parameter has no default, it's required
            if param.default == inspect.Parameter.empty:
                args_schema["required"].append(param_name)
    else:
        args_schema = parameters_override
    
    return {
        "tool_name": tool_name,
        "description": description,
        "parameters": args_schema,
        "function": func,
        "terminal": terminal,
        "tags": tags or []
    }