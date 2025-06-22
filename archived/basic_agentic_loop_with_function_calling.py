from litellm import completion
from typing import List, Dict
import os
import base64
import json

def list_files(directory_name: str) -> List[str]:
    """List files in the current directory."""
    return os.listdir(directory_name)

def read_file(directory_name: str, file_name: str) -> str:
    """Read a file's contents."""
    try:
        file_path = f"{directory_name}/{file_name}"
        with open(file_path, "r") as file:
            return file.read()
    except FileNotFoundError:
        return f"Error: {file_path} not found."
    except Exception as e:
        return f"Error: {str(e)}"


tool_functions = {
    "list_files": list_files,
    "read_file": read_file
}

tools = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "Returns a list of files in the directory.",
            "parameters": {
                "type": "object", 
                "properties": {"directory_name":{"type": "string"}}, 
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Reads the content of a specified file in the directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_name": {"type": "string"},
                    "directory_name":{"type": "string"}},
                "required": ["file_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "terminate",
            "description": "Terminates the conversation. No further actions or interactions are possible after this. Prints the provided message for the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                },
                "required": ["message"]
            }
        }
    }
]

# Our rules are simplified since we don't have to worry about getting a specific output format
agent_rules = [{
    "role": "system",
    "content": """
You are an AI agent that can perform tasks by using available tools. 

If a user asks about files, documents, or content, first list the files before reading them.
When you are done, terminate the conversation by using the "terminate" tool and I will provide the results to the user.
"""
}]

# Initialize agent parameters
iterations = 0
max_iterations = 5

user_task = input("What would you like me to do? ")

memory = [{"role": "user", "content": user_task}]

# The Agent Loophe 
while iterations < max_iterations:
    print(f"iterations: {iterations}")
    messages = agent_rules + memory

    response = completion(
        model="openai/gpt-4o",
        messages=messages,
        tools=tools,
        max_tokens=1024
    )

    print(response)

    if response.choices[0].message.tool_calls:
        print("reached 1")
        tool = response.choices[0].message.tool_calls[0]
        print(tool)
        tool_name = tool.function.name
        try:
            tool_args = json.loads(tool.function.arguments)
        except JSONDecodeError as e:
            print("error: No JSON object could be decoded")


        action = {
            "tool_name": tool_name,
            "args": tool_args
        }

        # if tool name is terminate, break out of the loop
        if tool_name == "terminate":
            print(f"Termination message: {tool_args['message']}")
            print("reached 2")
            break
        
        # if the tool is available
        elif tool_name in tool_functions:
            try:
                # run the tools
                result = {"result": tool_functions[tool_name](**tool_args)}
            except Exception as e:
                # output errors
                result = {"error":f"Error executing {tool_name}: {str(e)}"}
        else:
            # tool is not available
            result = {"error": f"Unknown tool: {tool_name}"}

        print(f"Executing: {tool_name} with args {tool_args}")
        print(f"Result: {result}")

        # add the response to the memory
        memory.extend([
            {"role": "assistant", "content": json.dumps(action)},
            {"role": "user", "content": json.dumps(result)}
        ])
    else:
        print("reached 3")
        result = response.choices[0].message.content
        print(f"Response: {result}")
        break
    iterations+=1