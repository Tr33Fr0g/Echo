import random
import ollama

# Echo's standing instructions, sent as the first message of every conversation
SYSTEM_PROMPT = """You are Echo, a personal assistant running locally on Bryan's PC.
You speak like a calm, capable butler, in the style of JARVIS and Alfred.

Rules:
- Answer the question first, plainly and accurately.
- Never invent facts. If you cannot check something, such as the weather, the time, or files, say you don't have access to it yet.
- Only mention facts about Bryan that he has stated in this conversation. Never infer or invent details about his habits, history, or surroundings.
- Dry humour is occasional: at most one short quip every 1-2 replies but back to back is fine if its mixed in, and never in place of the answer.
- Jokes may only use facts stated in this conversation or atleast shouldn't use lies. Never invent a detail to make a joke work.
- Keep replies short unless asked for detail.
- Do not use emojis.
- You are software. Never offer physical actions such as making drinks.
- Do not mention that you run locally or on this machine unless asked.
- Never claim to be running, processing, or doing something you cannot do. You can only chat for now.
Example of the correct style:
User: Who are you?
Echo: Echo: Echo, sir. Your assistant, running locally on this machine.
User: What's the weather?
Echo: I don't have access to weather data yet, sir.
User: I finally fixed that bug. Took me three tries.
Echo: Well done, sir. A personal best."""

# the conversation so far; the model only knows what is in this list
history = [{"role": "system", "content": SYSTEM_PROMPT}]
# startup greeting: one opening + one ending, picked at random (5 x 8 = 40 combos)
openings = [
    "Hello, sir.",
    "Greetings, sir.",
    "Welcome back, sir.",
    "Ah, there you are, sir.",
    "Systems online, sir.",
]

endings = [
    "Echo at your service.",
    "How may I assist you today?",
    "What can I do for you?",
    "What are we working on?",
    "I trust we are being productive today.",
    "Shall we get started?",
    "I was beginning to wonder.",
    "Ready when you are.",
]
greeting = f"{random.choice(openings)} {random.choice(endings)}"
print(f"Echo: {greeting}")
# main chat loop: runs until the user types /quit
while True:
    user_text = input("You: ")

    # commands are checked first so they are never sent to the model
    if user_text.lower() == "/quit":
        break
    elif user_text.lower() == "/help":
        print("""Commands: \n
/quit - exit the program \n
/reset - clear the conversation but keep the personality \n
/help - show this help message""")
        continue
    elif user_text.lower() == "/history":
        print(f"History length: {len(history)} messages")
        continue
    elif user_text.lower() == "/reset":
        history = [{"role": "system", "content": SYSTEM_PROMPT}]
        print("Echo: Memory successfully cleared, sir.")
        continue

    # save my message so Echo has context for later turns
    history.append({"role": "user", "content": user_text})

    # send the whole conversation; stream=True returns the reply in pieces
    stream = ollama.chat(
        model="qwen3.5:9b",
        messages=history,
        # skips the model's reasoning step (faster; may turn on later for hard questions)
        think=False,
        stream=True
    )

    # print each piece as it arrives and collect them into the full reply
    reply = ""
    print("Echo: ", end="", flush=True)
    for chunk in stream:
        piece = chunk["message"]["content"]
        print(piece, end="", flush=True)
        reply += piece
    print()

    # save Echo's reply so it remembers its own side of the conversation
    history.append({"role": "assistant", "content": reply})