from groq import Groq
from rich.console import Console
from rich.markdown import Markdown

console = Console()
client = Groq(api_key="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")

messages = []

def ask_groq(messages):
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


if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        messages.append({"role": "user", "content": user_input})
        print("Groq:", end=" ")
        ask_groq(messages)
        print()





# md_text = """
# # Heading

# **Bold text**, *italic text*, and `code`.

# - List item 1
# - List item 2
# """

