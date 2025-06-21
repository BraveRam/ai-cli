from groq import Groq
from rich.console import Console
from rich.markdown import Markdown
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

console = Console()
CONFIG_PATH = Path.home() / ".tc_config"

def get_api_key():
    if CONFIG_PATH.exists():
        return CONFIG_PATH.read_text().strip()
    else:
        key = input("Enter your Groq API key: ").strip()
        CONFIG_PATH.write_text(key)
        print("Saved API key to ~/.tc_config")
        return key
    
api_key = get_api_key()

client = Groq(api_key=api_key)

messages = []

def ask_groq(messages):
    try:
        completion = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=messages,
        temperature=1,
        max_completion_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,)
        
        response = ''
        for chunk in completion:
            response += chunk.choices[0].delta.content or ""
        messages.append({"role": "assistant", "content": response})
        console.print(Markdown(response), end="")
    except Exception as e:
        print(f"""\033[31mError: {e} - May be your api key is not working or try again later.
              The following might help:
              1. Check your API key in ~/.tc_config
              2. Ensure you have an active internet connection.
              3. Run this on windows(powershell): del $env:USERPROFILE/.tc_config
              4. Run this on linux and mac: rm ~/.tc_config
              5. then rerun the script to re-enter your API key.\033[0m""")
        exit(1)
        


if __name__ == "__main__":
    print("\033[32mWelcome to the chatbot - you can start chatting....\033[0m")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        messages.append({"role": "user", "content": user_input})
        print("Groq:", end=" ")
        ask_groq(messages)