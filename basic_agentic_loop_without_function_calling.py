from litellm import completion
from typing import List, Dict
import os
import base64
import json

def generate_response(messages: List[Dict]) -> str:
    """Call LLM to get response"""
    response = completion(
        model="openai/gpt-4o",
        messages=messages,
        max_tokens=1024
    )
    return response.choices[0].message.content


api_key = os.environ['OPENAI_API_KEY']
#print(api_key)

def list_files() -> List[str]:
    return [f for f in os.listdir('.') if os.path.isfile(os.path.join('.', f))]

def read_file(file_name: str) -> str:
    try:
        # Open the file in read mode
        file = open(file_name, "r")

        # Read the entire content of the file
        content = file.read()

        # Close the file
        file.close()
        return content
    except Exception as e:
        # Handle any exception, with access to the exception object
        print(f"An error occurred: {e}")
        return ""


def parse_action(response: str) -> str:
    """Extract code block from response"""
    if not '```' in response:
        return response

    action = response.split('```')[1].strip()
    if action.startswith("action"):
        action = action[6:]

    return json.loads(action)

agent_rules = [{
    "role": "system",
    "content": """
You are an AI agent that can perform tasks by using available tools.

Available tools:
- list_files() -> List[str]: List all files in the current directory.
- read_file(file_name: str) -> str: Read the content of a file.
- terminate(message: str): End the agent loop and print a summary to the user.

If a user asks about files, list them before reading.

Every response MUST have an action.
Respond in this format:

```action
{
    "tool_name": "insert tool_name",
    "args": {...fill in any required arguments here...}
}
"""}]

iterations = 0
max_iterations = 7
memory = []
# The Agent Loop
while iterations < max_iterations:

    # 1. Construct prompt: Combine agent rules with memory
    prompt = agent_rules + memory

    # 2. Generate response from LLM
    print("Agent thinking...")
    response = generate_response(prompt)
    print(f"Agent response: {response}")

    # 3. Parse response to determine action
    action = parse_action(response)
    print(action)

    result = "Action executed"

    if action["tool_name"] == "list_files":
        result = {"result":list_files()}
    elif action["tool_name"] == "read_file":
        result = {"result":read_file(action["args"]["file_name"])}
    elif action["tool_name"] == "error":
        result = {"error":action["args"]["message"]}
    elif action["tool_name"] == "terminate":
        print(action["args"]["message"])
        break
    else:
        result = {"error":"Unknown action: "+action["tool_name"]}

    print(f"Action result: {result}")

    # 5. Update memory with response and results
    memory.extend([
        {"role": "assistant", "content": response},
        {"role": "user", "content": json.dumps(result)}
    ])

    # 6. Check termination condition
    if action["tool_name"] == "terminate":
        break

    iterations += 1

