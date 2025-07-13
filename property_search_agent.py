from litellm import completion
import json
from module.register_tools import *
from module.game import *
from module.agent_language import *
from module.agent import *
import types


# action_registry.register(Action(
#     name="get_search_criteria",
#     function=get_search_criteria,
#     description="Prompt user for home search criteria and return them as a dictionary.",
#     parameters={},
#     terminal=False
# ))

# action_registry.register(Action(
#     name="search_property",
#     function=search_property,
#     description="search for property based on search_criteria, return the results as a list",
#     parameters={
#         "type": "object",
#         "properties": {
#             "search_criteria": {
#                 "type": "object", 
#                 "description": "search criteria used to search for the property"
#             },
#         },
#         "required": ["search_criteria"]
#     },
#     terminal=False
# ))


# action_registry.register(Action(
#     name="summarize_options",
#     function=summarize_options,
#     description="summarize the matched properties based on the properties features",
#     parameters={
#         "type": "object",
#         "properties": {
#             "search_results": {
#                 "type": "object", 
#                 "description": "search criteria used to search for the property"
#             },
#         },
#         "required": ["search_results"]
#     },
#     terminal=False
# ))


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
    tags=["get_search_criteria","search_property", "summarize_options"],
    tool_names=["get_search_criteria", "search_property", "summarize_options"]
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
final_memory = property_search_agent.run(user_input, max_iterations=5)

# Print the termination message (if any)
for item in final_memory.get_memories():
    print(f"\nMemory: {item['content']}")