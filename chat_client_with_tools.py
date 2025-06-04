import argparse
import requests
import json
import re
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
#

def main():
    parser = argparse.ArgumentParser(description="Send a chat message to a local AI server.")
    
    parser.add_argument("prompt", type=str, help="User prompt message (positional argument).")
    
    parser.add_argument("--url", type=str, default="http://localhost:1234/v1/chat/completions", help="URL of the chat completion endpoint.")
    parser.add_argument("--model", type=str, default="microsoft/phi-4-mini-reasoning", help="Model name to use.")
    # parser.add_argument("--system", type=str, default="Always answer in rhymes. Today is Thursday", help="System message.")
    parser.add_argument("--temperature", type=float, default=0.7, help="Temperature setting.")
    parser.add_argument("--max_tokens", type=int, default=-1, help="Maximum number of tokens.")
    # parser.add_argument("--stream", action='store_false', help="Whether to stream the output.")
    args = parser.parse_args()
    prompt = args.prompt
    messages = [
        {
            "role": "system",
            "content": "You are a helpful translator. Use the supplied tools to assist the user.",
        },
        {
            "role": "user",
            "content": "Translate this text to English and explain grammar usage of each word in the text by the provided tool: \"{}\"".format(prompt),
        },
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
    )
    message = response.choices[0].message.content
    pattern = r"<think>.*?</think>"
    cleanedMessage = re.sub(pattern, "", message or "")
 
    words = list(map(lambda tool: json.loads(tool.function.arguments).get("word"), response.choices[0].message.tool_calls or []))
    definitions = list(map(lambda word: get_grammar_definition(word), words))
    joined_message = "\n".join([cleanedMessage] + definitions)
    print(joined_message)
if __name__ == "__main__":
    main()
