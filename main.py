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

messages = [
    {
        "role": "system",
        "content": "You are an elevated, helpful, and knowledgeable assistant. Provide clear, concise, and accurate responses."
    }
]

loading = True

def spinner():
    spinner_chars = ['|', '/', '-', '\\']
    idx = 0
    while loading:
        text = f"Loading... {spinner_chars[idx]}"
        print(text.ljust(30), end='\r')
        idx = (idx + 1) % len(spinner_chars)
        time.sleep(0.1)

MODELS = [
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
    "deepseek-r1-distill-llama-70b",
    "meta-llama/llama-4-maverick-17b-128e-instruct",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "moonshotai/kimi-k2-instruct",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3-32b",
]

def select_model():
    print("Please select a model:")
    for i, model in enumerate(MODELS):
        print(f"{i + 1}. {model}")

    while True:
        try:
            choice = int(input(f"Enter a number (1-{len(MODELS)}): "))
            if 1 <= choice <= len(MODELS):
                return MODELS[choice - 1]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def get_groq_response(messages, model):
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=1,
            max_completion_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )
        response = ""
        for chunk in completion:
            response += chunk.choices[0].delta.content or ""
        return response
    except Exception as e:
        raise e


def ask_groq(messages, model):
    global loading
    response = ''
    thread = threading.Thread(target=spinner)

    try:
        loading = True
        thread.start()
        response = get_groq_response(messages, model)

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
    model = select_model()
    print(f"\nSelected model: {model}\n")
    print("\033[96mWelcome to the chatbot - you can start chatting....\033[0m")
    while True:
        console.print("**You:**", style="bold blue", end=" ")
        user_input = input()
        if user_input.lower() in ["exit", "quit"]:
            break
        messages.append({"role": "user", "content": user_input})
        print("Groq:", end=" ")
        ask_groq(messages, model)