import argparse
import re
from openai import OpenAI

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
#model = "qwen3-8b-mlx"
model = "qwen/qwen3-8b"

def detect_language(paragraph: str) -> str:
    messages = [
        {
            "role": "user",
            "content": "What is the language of this sentence (provide the language name without further explanation): \"{}\"".format(paragraph)
        }
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )

    returnedMessage = response.choices[0].message.content or "Error: Could not get response"
    cleaned_text = re.sub(r"<think>.*?</think>", "", returnedMessage, flags=re.DOTALL)
    return cleaned_text

def translate_to_english(paragraph: str) -> str:
    messages = [
        {
            "role": "user",
            "content": "Translate sentence by sentence to English this text: \"{}\"".format(paragraph),
        }
    ]
    
    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )

    returnedMessage = response.choices[0].message.content or "Error: Could not get response"
    cleaned_text = re.sub(r"<think>.*?</think>", "", returnedMessage, flags=re.DOTALL)
    return cleaned_text

def split_into_words(paragraph: str) -> str:
    messages = [
        {
            "role": "user",
            "content": "Split the paragraph into list of words without duplicates, each word per line without any other characters: \"{}\"".format(paragraph),
        }
    ]
    
    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )

    returnedMessage = response.choices[0].message.content or "Error: Could not get response"
    cleaned_text = re.sub(r"<think>.*?</think>", "", returnedMessage, flags=re.DOTALL)
    return cleaned_text

def define_each_word(word: str, language: str) -> str:
    messages = [
        {
            "role": "user",
            "content": "Give IPA Pronunciation and explain the grammar of this word ({}): \"{}\"".format(language, word),
        }
    ]
    
    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )

    returnedMessage = response.choices[0].message.content or "Error: Could not get response"
    cleaned_text = re.sub(r"<think>.*?</think>", "", returnedMessage, flags=re.DOTALL)
    return cleaned_text

def main():
    parser = argparse.ArgumentParser(description="Process a prompt and optional flags.")
    
    # Positional argument (required)
    parser.add_argument("prompt", type=str, help="The main input prompt.")
    
    # Optional flags
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output.")
    
    args = parser.parse_args()
    
    prompt = args.prompt

    language = detect_language(prompt)
    
    translated = translate_to_english(prompt)

    splitedLines = split_into_words(prompt)

    word_list = [line for line in splitedLines.splitlines() if line.strip()]
    
    definitions = list(map(lambda word: define_each_word(word, language), word_list))

    result = "\n".join([prompt, translated] + definitions)
    
    print(result)

if __name__ == "__main__":
    main()
