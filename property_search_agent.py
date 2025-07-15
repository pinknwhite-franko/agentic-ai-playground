from litellm import completion
import json
from module.register_tools import *
from module.game import *
from module.agent_language import *
from module.agent import *
import types


# Define clear goals for the agent
goals = [
    Goal(
        priority=1, 
        name="search property based on user inputted criteria", 
        description="search the property_data.json based on user criteria, return the matched property and provide a summary of the options. "
    ),
    Goal(
        priority=2, 
        name="Terminate", 
        description="Terminate the session when tasks are complete with a helpful summary"
    )
]

# Create and populate the action registry
action_registry = PythonActionRegistry(
    tags=["get_search_criteria","search_property", "summarize_options","system"],
    tool_names=["get_search_criteria", "search_property", "summarize_options", "terminate"]
)

# print the action registry for debugging
# for action in action_registry.get_actions():
#     function_data = {attr: value for attr, value in vars(action).items() if not isinstance(value, types.FunctionType)}
#     print(json.dumps(function_data, indent=4))

# Define the agent language and environment
agent_language = AgentFunctionCallingActionLanguage()
environment = Environment()
#generate_response = "Hello, Are you looking for a house?"

# Create the agent
property_search_agent = Agent(
    goals=goals,
    agent_language=agent_language,
    action_registry=action_registry,
    generate_response=generate_response,
    environment=environment
)

# Run the agent
user_input = "search for a property based on my criteria and provide a summary of the options"
final_memory = property_search_agent.run(user_input, max_iterations=6)

# Print the termination message (if any)
for item in final_memory.get_memories():
    print(f"\nMemory: {item['content']}")