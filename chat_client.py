import argparse
import requests
import json

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

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        #"model": args.model,
        "messages": [
            # {"role": "system", "content": args.system},
            {"role": "user", "content": args.prompt}
        ],
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
        "stream": False
        # "stream": args.stream
    }

    response = requests.post(args.url, headers=headers, json=data)

    if 'application/json' in response.headers.get('Content-Type', ''):
        data = response.json()
        print(data['choices'][0]['message']['content'])
    else:
        print("Not a JSON response:", response.text)


    # try:
    #     print(json.dumps(response.json().choices[0].message.content, indent=2))
    # except Exception as e:
    #     print(f"Error parsing response: {e}")
    #     # print(response.text)

if __name__ == "__main__":
    main()
