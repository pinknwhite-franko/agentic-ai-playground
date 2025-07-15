import json
from typing import List, Dict
import inspect
from typing import get_type_hints
import module.config as config

# =============================================
# Define the decorator for registering tools
# =============================================
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

# =============================================
# Registering tools with the decorator
# =============================================
@register_tool(tags=["get_search_criteria"])
def get_search_criteria() -> dict:
    """Prompt user for home search criteria and return them as a dictionary."""
    location = input("Enter the desired location (e.g., Sloan Lake, Denver): ").strip()
    
    try:
        num_of_bedrooms = int(input("Enter the number of bedrooms: "))
    except ValueError:
        num_of_bedrooms = None
    
    try:
        num_of_bathrooms = int(input("Enter the number of bathrooms: "))
    except ValueError:
        num_of_bathrooms = None

    has_garage_input = input("Do you want a garage? (yes/no): ").strip().lower()
    if has_garage_input in ['yes', 'y']:
        has_garage = True
    elif has_garage_input in ['no', 'n']:
        has_garage = False
    else:
        raise ValueError("Invalid input for garage preference. Please enter 'yes' or 'no'.")
    
    try:
        year_built = int(input("Enter the minimum year built (e.g., 1970): "))
    except ValueError:
        year_built = None
    
    try:
        partial_search_input = input("Do you want to include the properties that does't match all the criteria? (yes/no): ").strip().lower()
        if partial_search_input in ['yes', 'y', '1']:
            partial_search = True
        elif partial_search_input in ['no', 'n', '0']:
            partial_search = False
        else:
            raise ValueError("Invalid input for partial search.")
    except ValueError:
        partial_search = None

    return {
        "search_criteria":{
            "location": location,
            "num_of_bedrooms": num_of_bedrooms,
            "num_of_bathrooms": num_of_bathrooms,
            "has_garage": has_garage,
            "year_built": year_built
        },
        "partial_search": partial_search
    }



@register_tool(tags=["search_property"])
def search_property(search_criteria: str, partial_search: bool) -> list[dict]:
    """search for property based on a set of criterias"""
    file_path = "./data/property_data.json"

    search_criteria = json.loads(search_criteria)

    with open(file_path, "r") as f:
        properties = json.load(f)
    
    def partial_search_property(prop, criteria):
        return all(prop.get(k) == v if k != "year_built" else prop.get(k) >= v for k, v in criteria.items())
    
    #partial_search = True
    if partial_search:
        matches = [prop for prop in properties if partial_search_property(prop, search_criteria)]
        print(matches)
    else :
        matches = []
        for prop in properties:
            if (
                prop["location"] == search_criteria["location"] and
                prop["num_of_bedrooms"] == search_criteria["num_of_bedrooms"] and
                prop["num_of_bathrooms"] == search_criteria["num_of_bathrooms"] and
                prop["has_garage"] == search_criteria["has_garage"] and
                prop["year_built"] > search_criteria["year_built"]
            ):
                matches.append(prop)
    return { "search_results " : matches} if matches else {["No properties found matching the criteria."]}
    
@register_tool(tags=["summarize_options"])
def summarize_options(search_results: list[dict]) -> list[dict]:
    """summarize the matched properties based on the properties features"""
    if not search_results:
        return [{"instrustion":"No properties found matching the criteria."}]
    else:
        return {"search_results": search_results, "instrustion":"Here are the matched properties based on the criteria, could you compare these properties? terminate the session with a helpful summary."}

@register_tool(tags=["system"], terminal=True)
def terminate(message: str) -> str:
    """Terminates the agent's execution with a final message.

    Args:
        message: The final message to return before terminating

    Returns:
        The message with a termination note appended
    """
    return f"{message}\nTerminating..."

# def search_in_file(file_name: str, search_term: str) -> list:
#     """Search for a term in a file and return matching lines."""
#     results = []
#     with open(file_name, 'r') as f:
#         for i, line in enumerate(f.readlines()):
#             if search_term in line:
#                 results.append((i+1, line.strip()))
#     return results