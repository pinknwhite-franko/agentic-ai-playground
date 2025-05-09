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


first_prompt = input("what function you want to create?")

messages = [
   {"role": "system", "content": "You are an expert software engineer that prefers python programming."},
   {"role": "user", "content": first_prompt}
]

response = generate_response(messages)
print(response)
print("------")

second_prompt = input("what documentatin you would like to add to this code?")
messages.append({"role": "assistant", "content": response})
messages.append({"role": "user", "content": second_prompt})

response = generate_response(messages)
print(response)
print("------")

second_prompt = input("Let's add some test cases. What should our test cover?")
messages.append({"role": "assistant", "content": response})
messages.append({"role": "user", "content": second_prompt})

response = generate_response(messages)
print(response)
print("------")

