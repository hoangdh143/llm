from datetime import datetime, timedelta
import json
import random
from openai import OpenAI

# Point to the local server
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
#model = "lmstudio-community/qwen2.5-7b-instruct"
model = "qwen/qwen3-8b"

def get_grammar_definition(word: str) -> str:
    messages = [{
        "role": "user",
        "content": "Provide IPA Pronunication and explain grammar usage of \"{}\"".format(word)
    }]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    return response.choices[0].message.content

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_grammar_definition",
            "description": "Get IPA pronunciation and grammar usage of single word",
            "parameters": {
                "type": "object",
                "properties": {
                    "word": {
                        "type": "string",
                        "description": "The word to be defined"
                    }
                },
                "required": ["word"],
                "additionalProperties": False,
            }
        }
    }
]
# def get_delivery_date(order_id: str) -> datetime:
#     # Generate a random delivery date between today and 14 days from now
    # in a real-world scenario, this function would query a database or API
    # today = datetime.now()
    # random_days = random.randint(1, 14)
    # delivery_date = today + timedelta(days=random_days)
    # print(
        # f"\nget_delivery_date function returns delivery date:\n\n{delivery_date}",
        # flush=True,
    # )
    # return delivery_date


# tools = [
    # {
    #     "type": "function",
        # "function": {
        #     "name": "get_delivery_date",
            # "description": "Get the delivery date for a customer's order. Call this whenever you need to know the delivery date, for example when a customer asks 'Where is my package'",
            # "parameters": {
            #     "type": "object",
                # "properties": {
                #     "order_id": {
                        # "type": "string",
                        # "description": "The customer's order ID.",
                #     },
                # },
                # "required": ["order_id"],
                # "additionalProperties": False,
        #     },
        # },
#     }
# ]

messages = [
    {
        "role": "system",
        "content": "You are a helpful customer support assistant. Use the supplied tools to assist the user.",
    },
    {
        "role": "user",
        "content": "Translate this sentence to English and explain grammar usage of each word in the sentence by the provided tool: \"Das Gefieder ist vorwiegend dunkel olivbraun\"",
    },
]

# LM Studio
response = client.chat.completions.create(
    model=model,
    messages=messages,
    tools=tools,
)

print("\nModel response requesting tool call:\n", flush=True)
print(response, flush=True)

# Extract the arguments for get_delivery_date
# Note this code assumes we have already determined that the model generated a function call.
tool_call = response.choices[0].message.tool_calls[0]
arguments = json.loads(tool_call.function.arguments)

word = arguments.get("word")

# Call the get_delivery_date function with the extracted order_id
grammarExplained = get_grammar_definition(word)

assistant_tool_call_request_message = {
    "role": "assistant",
    "tool_calls": [
        {
            "id": response.choices[0].message.tool_calls[0].id,
            "type": response.choices[0].message.tool_calls[0].type,
            "function": response.choices[0].message.tool_calls[0].function,
        }
    ],
}

# Create a message containing the result of the function call
function_call_result_message = {
    "role": "tool",
    "content": json.dumps(
        {
            "word": word,
            "grammar_usage": grammarExplained,
        }
    ),
    "tool_call_id": response.choices[0].message.tool_calls[0].id,
}

# Prepare the chat completion call payload
completion_messages_payload = [
    messages[0],
    messages[1],
    assistant_tool_call_request_message,
    function_call_result_message,
]

# Call the OpenAI API's chat completions endpoint to send the tool call result back to the model
# LM Studio
response = client.chat.completions.create(
    model=model,
    messages=completion_messages_payload,
)

print("\nFinal model response with knowledge of the tool call result:\n", flush=True)
print(response.choices[0].message.content, flush=True)


