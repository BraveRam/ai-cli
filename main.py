from groq import Groq
from rich.console import Console
from rich.markdown import Markdown
from dotenv import load_dotenv
from pathlib import Path
import time
import threading

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

loading = True

def spinner():
    spinner_chars = ['|', '/', '-', '\\']
    idx = 0
    while loading:
        text = f"Loading... {spinner_chars[idx]}"
        print(text.ljust(30), end='\r')
        idx = (idx + 1) % len(spinner_chars)
        time.sleep(0.1)

def ask_groq(messages):
    global loading
    response = ''
    thread = threading.Thread(target=spinner)

    try:
        loading = True
        thread.start()

        completion = client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",
            messages=messages,
            temperature=1,
            max_completion_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )

        for chunk in completion:
            response += chunk.choices[0].delta.content or ""

    except Exception as e:
        print(' ' * 30, end='\r')
        print(f"""\033[31mError: {e} - May be your API key is not working or try again later.
1. Check your API key in ~/.tc_config
2. Ensure you have an active internet connection.
3. Run this on Windows (PowerShell): del $env:USERPROFILE/.tc_config
4. Run this on Linux/macOS: rm ~/.tc_config
5. Then re-run the script to re-enter your API key.\033[0m""")
        loading = False
        thread.join()
        exit(1)

    loading = False
    thread.join()
    print(' ' * 30, end='\r')
    console.print(Markdown(response), end="")
    messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    print("\033[96mWelcome to the chatbot - you can start chatting....\033[0m")
    while True:
        console.print("**You:**", style="bold blue", end=" ")
        user_input = input()
        if user_input.lower() in ["exit", "quit"]:
            break
        messages.append({"role": "user", "content": user_input})
        print("Groq:", end=" ")
        ask_groq(messages)